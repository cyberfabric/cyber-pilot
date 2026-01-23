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
            exit_code = main(["validate", "--skip-code-traceability"])
            # Exit code 0 = PASS, 2 = FAIL - both are valid (not argument error)
            self.assertIn(exit_code, [0, 2])

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

    def test_validate_code_root_with_features_parsing(self):
        """Cover --features parsing when validating a code root directory."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            (root / "architecture" / "features" / "feature-a").mkdir(parents=True)
            (root / "architecture" / "features" / "feature-b").mkdir(parents=True)

            # Minimal artifacts for feature-a/feature-b so traceability runs.
            (root / "architecture" / "features" / "feature-a" / "DESIGN.md").write_text("# Feature: A\n", encoding="utf-8")
            (root / "architecture" / "features" / "feature-a" / "CHANGES.md").write_text("# Implementation Plan: A\n", encoding="utf-8")
            (root / "architecture" / "features" / "feature-b" / "DESIGN.md").write_text("# Feature: B\n", encoding="utf-8")
            (root / "architecture" / "features" / "feature-b" / "CHANGES.md").write_text("# Implementation Plan: B\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["validate", "--artifact", str(root), "--features", "feature-a, b, ,feature-b", "--skip-fs-checks"])

            self.assertIn(exit_code, (0, 2))
            out = json.loads(stdout.getvalue())
            self.assertIn("status", out)

    def test_validate_requires_requirements_file_exists(self):
        """Cover SystemExit when requirements file path does not exist."""
        with TemporaryDirectory() as tmpdir:
            art = Path(tmpdir) / "DESIGN.md"
            art.write_text("# Technical Design\n\n## A. X\n", encoding="utf-8")
            missing_req = Path(tmpdir) / "missing-req.md"

            with self.assertRaises(SystemExit):
                main(["validate", "--artifact", str(art), "--requirements", str(missing_req)])

    def test_validate_writes_output_file(self):
        """Cover --output branch (writes JSON report to file)."""
        with TemporaryDirectory() as tmpdir:
            td = Path(tmpdir)
            art = td / "DESIGN.md"
            art.write_text("# Technical Design\n\n## A. X\n", encoding="utf-8")
            req = td / "req.md"
            req.write_text("### Section A: a\n", encoding="utf-8")

            out_path = td / "out.json"
            exit_code = main(["validate", "--artifact", str(art), "--requirements", str(req), "--output", str(out_path)])
            self.assertIn(exit_code, (0, 2))
            self.assertTrue(out_path.exists())

    def test_validate_dir_mode_writes_output_file(self):
        """Cover --output branch when --artifact is a directory."""
        with TemporaryDirectory() as tmpdir:
            td = Path(tmpdir)
            (td / ".git").mkdir()
            (td / "architecture" / "features" / "feature-a").mkdir(parents=True)
            (td / "architecture" / "features" / "feature-a" / "DESIGN.md").write_text("# Feature: A\n", encoding="utf-8")
            (td / "architecture" / "features" / "feature-a" / "CHANGES.md").write_text("# Implementation Plan: A\n", encoding="utf-8")

            out_path = td / "out.json"
            exit_code = main(["validate", "--artifact", str(td), "--output", str(out_path), "--skip-fs-checks"])
            self.assertIn(exit_code, (0, 2))
            self.assertTrue(out_path.exists())

    def test_validate_feature_dir_with_design_md_runs_codebase_traceability(self):
        """Cover validate branch when --artifact is a feature directory containing DESIGN.md."""
        with TemporaryDirectory() as tmpdir:
            feat = Path(tmpdir) / "architecture" / "features" / "feature-x"
            feat.mkdir(parents=True)
            (feat / "DESIGN.md").write_text("# Feature: X\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["validate", "--artifact", str(feat), "--skip-fs-checks"])
            self.assertIn(exit_code, (0, 2))
            out = json.loads(stdout.getvalue())
            self.assertIn("artifact_kind", out)


class TestCLISearchCommands(unittest.TestCase):
    """Test search command variations."""

    def test_list_sections_basic(self):
        """Test list-sections command."""
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("""# Document

## A. First Section

Content

## B. Second Section

More content
""")
            
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["list-sections", "--artifact", str(doc)])
            
            self.assertEqual(exit_code, 0)
            output = json.loads(stdout.getvalue())
            self.assertIn("entries", output)
            self.assertGreater(len(output["entries"]), 0)

    def test_list_ids_basic(self):
        """Test list-ids command."""
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("""# Document

**ID**: `fdd-test-actor-user`

**ID**: `fdd-test-capability-login`
""")
            
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["list-ids", "--artifact", str(doc)])
            
            self.assertEqual(exit_code, 0)
            output = json.loads(stdout.getvalue())
            self.assertIn("ids", output)
            self.assertEqual(len(output["ids"]), 2)

    def test_list_ids_missing_file_errors(self):
        """Cover list-ids load_text error branch."""
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["list-ids", "--artifact", "/tmp/does-not-exist.md"])
        self.assertEqual(exit_code, 1)

    def test_list_ids_with_pattern(self):
        """Test list-ids with pattern filter."""
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("""# Document

**ID**: `fdd-test-actor-user`
**ID**: `fdd-test-actor-admin`
**ID**: `fdd-test-capability-login`
""")
            
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                # Use = form for pattern starting with dash
                exit_code = main(["list-ids", "--artifact", str(doc), "--pattern=-actor-"])
            
            self.assertEqual(exit_code, 0)
            output = json.loads(stdout.getvalue())
            self.assertEqual(len(output["ids"]), 2)

    def test_search_literal(self):
        """Test search command with literal query."""
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("""# Document

This is a test document.

Test appears twice in this test.
""")
            
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["search", "--artifact", str(doc), "--query", "test"])
            
            self.assertEqual(exit_code, 0)
            output = json.loads(stdout.getvalue())
            self.assertIn("hits", output)
            self.assertGreater(len(output["hits"]), 0)

    def test_search_regex(self):
        """Test search command with regex query."""
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("""# Document

test123
test456
other
""")
            
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["search", "--artifact", str(doc), "--query", r"test\d+", "--regex"])
            
            self.assertEqual(exit_code, 0)
            output = json.loads(stdout.getvalue())
            self.assertEqual(len(output["hits"]), 2)

    def test_where_used_with_regex_query_components(self):
        """Cover where-used parsing for trace query with phase/inst."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            doc = tmppath / "doc.md"
            doc.write_text("x fdd-test-req-auth:ph-1:inst-step\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["where-used", "--root", str(tmppath), "--id", "fdd-test-req-auth:ph-1:inst-step"])

            self.assertEqual(exit_code, 0)
            output = json.loads(stdout.getvalue())
            self.assertEqual(output.get("phase"), "ph-1")
            self.assertEqual(output.get("inst"), "inst-step")

    def test_list_sections_missing_file_errors(self):
        """Cover error path when artifact file can't be loaded."""
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["list-sections", "--artifact", "/tmp/does-not-exist.md"])
        self.assertEqual(exit_code, 1)

    def test_list_ids_under_heading_not_found(self):
        """Cover NOT_FOUND branch for --under-heading."""
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Doc\n\n## A\n\n**ID**: `fdd-test-actor-user`\n", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["list-ids", "--artifact", str(doc), "--under-heading", "Missing"])
            self.assertEqual(exit_code, 1)

    def test_list_ids_under_heading_found(self):
        """Cover FOUND branch for --under-heading with base_offset adjustment."""
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text(
                "\n".join(
                    [
                        "# Doc",
                        "",
                        "## A",
                        "",
                        "**ID**: `fdd-test-actor-user`",
                        "",
                        "## B",
                        "",
                        "**ID**: `fdd-test-actor-admin`",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["list-ids", "--artifact", str(doc), "--under-heading", "A"])
            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("count"), 1)
            self.assertEqual(out.get("ids")[0].get("id"), "fdd-test-actor-user")

    def test_read_section_change_wrong_kind(self):
        """Cover --change only valid for CHANGES.md."""
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Doc\n", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["read-section", "--artifact", str(doc), "--change", "1"])
            self.assertEqual(exit_code, 1)

    def test_read_section_section_not_found(self):
        """Cover NOT_FOUND for --section."""
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Doc\n\n## A. A\n\nX\n", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["read-section", "--artifact", str(doc), "--section", "B"])
            self.assertEqual(exit_code, 1)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "NOT_FOUND")

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

            dst = wf_dir / "fdd-business-context.md"
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

    def test_get_item_delegates_to_read_section(self):
        """Cover get-item delegating to read-section."""
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Doc\n\n## A. A\n\nX\n", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["get-item", "--artifact", str(doc), "--section", "A"])
            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "FOUND")

    def test_list_items_under_heading_not_found(self):
        """Cover NOT_FOUND branch for list-items --under-heading."""
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Doc\n\n## A\n\n**ID**: `fdd-test-actor-user`\n", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["list-items", "--artifact", str(doc), "--under-heading", "Missing"])
            self.assertEqual(exit_code, 1)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out["status"], "NOT_FOUND")

    def test_list_items_under_heading_found(self):
        """Cover list-items --under-heading FOUND path."""
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "BUSINESS.md"
            doc.write_text(
                "\n".join(
                    [
                        "# Business Context",
                        "",
                        "## B. Actors",
                        "",
                        "#### Admin",
                        "**ID**: `fdd-test-actor-admin`",
                        "**Role**: Admin",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["list-items", "--artifact", str(doc), "--under-heading", "B. Actors", "--lod", "id"])
            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("count"), 1)
            self.assertEqual(out.get("items")[0].get("id"), "fdd-test-actor-admin")


class TestCLITraceabilityCommands(unittest.TestCase):
    """Test traceability command variations."""

    def test_scan_ids_basic(self):
        """Test scan-ids command."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create test file with IDs
            doc = tmppath / "doc.md"
            doc.write_text("**ID**: `fdd-test-actor-user`\n")
            
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["scan-ids", "--root", str(tmppath)])
            
            self.assertEqual(exit_code, 0)
            output = json.loads(stdout.getvalue())
            self.assertIn("ids", output)
            self.assertGreater(len(output["ids"]), 0)

    def test_scan_ids_with_kind_filter(self):
        """Test scan-ids with kind filter."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            doc = tmppath / "doc.md"
            doc.write_text("""**ID**: `fdd-test-actor-user`
ADR-0001
""")
            
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["scan-ids", "--root", str(tmppath), "--kind", "fdd"])
            
            self.assertEqual(exit_code, 0)
            output = json.loads(stdout.getvalue())
            # Should only find FDD IDs, not ADR
            fdd_ids = [id_obj["id"] for id_obj in output["ids"]]
            self.assertIn("fdd-test-actor-user", fdd_ids)
            self.assertNotIn("ADR-0001", fdd_ids)

    def test_where_used_basic(self):
        """Test where-used command."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create file with ID usage
            doc = tmppath / "doc.md"
            doc.write_text("""
Reference to fdd-test-req-auth in doc.

Another reference to fdd-test-req-auth here.
""")
            
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["where-used", "--root", str(tmppath), "--id", "fdd-test-req-auth"])
            
            self.assertEqual(exit_code, 0)
            output = json.loads(stdout.getvalue())
            self.assertIn("hits", output)
            self.assertEqual(len(output["hits"]), 2)

    def test_where_defined_and_where_used_with_definition_filtering(self):
        """Cover where-defined FOUND and where-used filtering out definition lines."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
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

            # Usage file
            use = root / "notes.md"
            use.write_text("ref fdd-test-req-auth\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["where-defined", "--root", str(root), "--id", "fdd-test-req-auth"])
            self.assertIn(exit_code, (0, 2))
            out = json.loads(stdout.getvalue())
            self.assertIn(out["status"], ("FOUND", "AMBIGUOUS"))

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["where-used", "--root", str(root), "--id", "fdd-test-req-auth"])
            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            # Should not count the definition line in DESIGN.md as usage
            self.assertGreaterEqual(len(out.get("hits", [])), 1)

    def test_where_defined_not_found(self):
        """Cover where-defined NOT_FOUND branch."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "architecture").mkdir(parents=True)
            (root / "architecture" / "DESIGN.md").write_text("# Design\n", encoding="utf-8")

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["where-defined", "--root", str(root), "--id", "fdd-missing-id"])

            self.assertIn(exit_code, (1, 2))


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
    def test_list_items_load_error(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["list-items", "--artifact", "/tmp/does-not-exist.md"])
        self.assertEqual(code, 1)

    def test_read_section_load_error(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["read-section", "--artifact", "/tmp/does-not-exist.md", "--section", "A"])
        self.assertEqual(code, 1)

    def test_read_section_feature_id_branches(self):
        from fdd import cli as fdd_cli

        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "FEATURES.md"
            p.write_text("x\n", encoding="utf-8")

            stdout = io.StringIO()
            with unittest.mock.patch.object(fdd_cli, "read_feature_entry", return_value=None):
                with redirect_stdout(stdout):
                    code = main(["read-section", "--artifact", str(p), "--feature-id", "fdd-x-feature-y"])
            self.assertEqual(code, 1)

            stdout = io.StringIO()
            with unittest.mock.patch.object(fdd_cli, "read_feature_entry", return_value=(0, 1)):
                with redirect_stdout(stdout):
                    code = main(["read-section", "--artifact", str(p), "--feature-id", "fdd-x-feature-y"])
            self.assertEqual(code, 0)

    def test_read_section_change_branches(self):
        from fdd import cli as fdd_cli

        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "CHANGES.md"
            p.write_text("x\n", encoding="utf-8")

            stdout = io.StringIO()
            with unittest.mock.patch.object(fdd_cli, "read_change_block", return_value=None):
                with redirect_stdout(stdout):
                    code = main(["read-section", "--artifact", str(p), "--change", "1"])
            self.assertEqual(code, 1)

            stdout = io.StringIO()
            with unittest.mock.patch.object(fdd_cli, "read_change_block", return_value=(0, 1)):
                with redirect_stdout(stdout):
                    code = main(["read-section", "--artifact", str(p), "--change", "1"])
            self.assertEqual(code, 0)

    def test_read_section_heading_branch(self):
        from fdd import cli as fdd_cli

        with TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "DESIGN.md"
            p.write_text("x\n", encoding="utf-8")

            stdout = io.StringIO()
            with unittest.mock.patch.object(fdd_cli, "read_heading_block_by_title", return_value=None):
                with redirect_stdout(stdout):
                    code = main(["read-section", "--artifact", str(p), "--heading", "X"])
            self.assertEqual(code, 1)

            stdout = io.StringIO()
            with unittest.mock.patch.object(fdd_cli, "read_heading_block_by_title", return_value=(0, 1)):
                with redirect_stdout(stdout):
                    code = main(["read-section", "--artifact", str(p), "--heading", "X"])
            self.assertEqual(code, 0)

    def test_get_item_branches_delegate(self):
        from fdd import cli as fdd_cli

        with unittest.mock.patch.object(fdd_cli, "_cmd_read_section", return_value=0):
            self.assertEqual(main(["get-item", "--artifact", "x", "--section", "A"]), 0)
        with unittest.mock.patch.object(fdd_cli, "_cmd_read_section", return_value=0):
            self.assertEqual(main(["get-item", "--artifact", "x", "--heading", "H"]), 0)
        with unittest.mock.patch.object(fdd_cli, "_cmd_read_section", return_value=0):
            self.assertEqual(main(["get-item", "--artifact", "x", "--feature-id", "fdd-x-feature-y"]), 0)
        with unittest.mock.patch.object(fdd_cli, "_cmd_read_section", return_value=0):
            self.assertEqual(main(["get-item", "--artifact", "x", "--change", "1"]), 0)

    def test_find_id_and_search_load_error(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["find-id", "--artifact", "/tmp/does-not-exist.md", "--id", "x"])
        self.assertEqual(code, 1)

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["search", "--artifact", "/tmp/does-not-exist.md", "--query", "x"])
        self.assertEqual(code, 1)

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
            target = (fdd_root / "workflows" / "business-context.md").resolve()
            target_rel = fdd_cli._safe_relpath(target, root)

            misnamed = wf_dir / "foo.md"
            misnamed.write_text(
                "\n".join(
                    [
                        "# /fdd-business-context",
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

            expected_dst = wf_dir / "fdd-business-context.md"
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
            target = (fdd_root / "workflows" / "business-context.md").resolve()
            target_rel = fdd_cli._safe_relpath(target, root)

            misnamed = wf_dir / "foo.md"
            misnamed.write_text(f"# /fdd-business-context\n\nALWAYS open and follow `{target_rel}`\n", encoding="utf-8")

            dst = wf_dir / "fdd-business-context.md"
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

    def test_list_fdd_workflows_missing_dir_raises_system_exit(self):
        from fdd import cli as fdd_cli

        with TemporaryDirectory() as tmpdir:
            with self.assertRaises(SystemExit):
                fdd_cli._list_fdd_workflows(Path(tmpdir))

    def test_looks_like_generated_proxy_true_false(self):
        from fdd import cli as fdd_cli

        self.assertTrue(fdd_cli._looks_like_generated_proxy("ALWAYS open and follow `x`\n", "x"))
        self.assertFalse(fdd_cli._looks_like_generated_proxy("ALWAYS open and follow `y`\n", "x"))

    def test_list_fdd_workflows_skips_non_workflow_and_handles_read_error(self):
        from fdd import cli as fdd_cli

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            workflows = root / "workflows"
            workflows.mkdir()
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
                names = fdd_cli._list_fdd_workflows(root)
            self.assertEqual(names, ["ok"])

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

    def test_missing_required_option(self):
        """Test CLI command with missing required option."""
        stdout = io.StringIO()
        stderr = io.StringIO()
        
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                exit_code = main(["search", "--artifact", "/tmp/test.md"])
                # Missing --query
                self.assertNotEqual(exit_code, 0)
            except SystemExit as e:
                # argparse calls sys.exit on missing required arg
                self.assertNotEqual(e.code, 0)

    def test_empty_command(self):
        """Test CLI with no command."""
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main([])
        
        self.assertNotEqual(exit_code, 0)
        output = json.loads(stdout.getvalue())
        self.assertEqual(output["status"], "ERROR")
        self.assertIn("Missing subcommand", output["message"])

    def test_read_section_feature_id_wrong_kind(self):
        """Cover --feature-id only valid for FEATURES.md."""
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Doc\n", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["read-section", "--artifact", str(doc), "--feature-id", "fdd-x-feature-y"])
            self.assertEqual(exit_code, 1)

    def test_read_section_heading_not_found(self):
        """Cover NOT_FOUND for --heading."""
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Doc\n\n## A. A\n\nX\n", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["read-section", "--artifact", str(doc), "--heading", "Missing"])
            self.assertEqual(exit_code, 1)

    def test_find_id_not_found(self):
        """Cover NOT_FOUND for find-id."""
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Doc\n\n**ID**: `fdd-test-actor-user`\n", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["find-id", "--artifact", str(doc), "--id", "fdd-missing"])
            self.assertEqual(exit_code, 1)

    def test_find_id_found(self):
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Doc\n\n**ID**: `fdd-test-actor-user`\n", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["find-id", "--artifact", str(doc), "--id", "fdd-test-actor-user"])
            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "FOUND")
            self.assertIn("payload", out)
            self.assertIsNone(out.get("payload"))

    def test_find_id_found_with_payload(self):
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text(
                "\n".join(
                    [
                        "# Doc",
                        "",
                        "**ID**: `fdd-test-actor-user`",
                        "",
                        "---",
                        "payload-line",
                        "---",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["find-id", "--artifact", str(doc), "--id", "fdd-test-actor-user"])
            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "FOUND")
            payload = out.get("payload")
            self.assertIsInstance(payload, dict)
            self.assertEqual(payload.get("open_line"), 5)
            self.assertEqual(payload.get("close_line"), 7)
            self.assertEqual(payload.get("text"), "payload-line")

    def test_read_section_id_delegates_to_find_id(self):
        """Cover read-section --id delegation."""
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Doc\n\n**ID**: `fdd-test-actor-user`\n", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["read-section", "--artifact", str(doc), "--id", "fdd-test-actor-user"])
            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "FOUND")

    def test_get_item_id_delegates_to_find_id(self):
        """Cover get-item --id delegation."""
        with TemporaryDirectory() as tmpdir:
            doc = Path(tmpdir) / "doc.md"
            doc.write_text("# Doc\n\n**ID**: `fdd-test-actor-user`\n", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["get-item", "--artifact", str(doc), "--id", "fdd-test-actor-user"])
            self.assertEqual(exit_code, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out.get("status"), "FOUND")


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


if __name__ == "__main__":
    unittest.main()
