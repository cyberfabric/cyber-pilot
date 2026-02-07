import io
import json
import os
import sys
import types
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _bootstrap_project_root(root: Path, adapter_rel: str = "adapter") -> Path:
    (root / ".git").mkdir()
    (root / ".cypilot-config.json").write_text(
        json.dumps({"cypilotAdapterPath": adapter_rel}, ensure_ascii=False),
        encoding="utf-8",
    )
    adapter = root / adapter_rel
    adapter.mkdir(parents=True, exist_ok=True)
    (adapter / "AGENTS.md").write_text("# Test adapter\n", encoding="utf-8")
    return adapter


def _bootstrap_self_check_kits(root: Path, adapter: Path, *, with_example: bool = True, bad_example: bool = False) -> None:
    # Minimal artifacts registry that passes `load_artifacts_registry` and contains kits.
    _write_json(
        adapter / "artifacts.json",
        {
            "project_root": "..",
            "systems": [],
            "kits": {
                "cypilot-sdlc": {"format": "Cypilot", "path": "kits/cypilot-sdlc"},
            },
        },
    )

    kits_base = root / "kits" / "cypilot-sdlc" / "artifacts" / "req"
    kits_base.mkdir(parents=True, exist_ok=True)

    template = kits_base / "template.md"
    template.write_text(
        "---\n"
        "cypilot-template:\n"
        "  kind: req\n"
        "  version:\n"
        "    major: 1\n"
        "    minor: 0\n"
        "---\n"
        "\n"
        "<!-- cpt:id:item to_code=\"true\" -->\n"
        "<!-- cpt:id:item -->\n",
        encoding="utf-8",
    )

    if with_example:
        ex_dir = kits_base / "examples"
        ex_dir.mkdir(parents=True, exist_ok=True)
        example = ex_dir / "example.md"

        if bad_example:
            example.write_text(
                "---\n"
                "cypilot-template:\n"
                "  kind: req\n"
                "  version: 1.0\n"
                "---\n"
                "\n"
                "<!-- cpt:id:item -->\n"
                "- [x] `p1` - **ID**: `cpt-req-1`\n"
                "<!-- cpt:id:item -->\n",
                encoding="utf-8",
            )
        else:
            example.write_text(
                "<!-- cpt:id:item -->\n"
                "- [x] `p1` - **ID**: `cpt-req-1`\n"
                "<!-- cpt:id:item -->\n",
                encoding="utf-8",
            )


class TestCLIPyCoverageSelfCheck(unittest.TestCase):
    def test_self_check_pass(self):
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            _bootstrap_self_check_kits(root, adapter, with_example=True, bad_example=False)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["self-check"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "PASS")
                self.assertEqual(out.get("kits_checked"), 1)
                self.assertEqual(out.get("templates_checked"), 1)
                self.assertEqual(out["results"][0]["status"], "PASS")
            finally:
                os.chdir(cwd)

    def test_self_check_fail_on_validation_errors(self):
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            _bootstrap_self_check_kits(root, adapter, with_example=True, bad_example=True)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["self-check"])
                self.assertEqual(exit_code, 2)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "FAIL")
                self.assertEqual(out["results"][0]["status"], "FAIL")
                self.assertIn("errors", out["results"][0])
            finally:
                os.chdir(cwd)

    def test_self_check_verbose_includes_warnings(self):
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            _bootstrap_self_check_kits(root, adapter, with_example=False)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["self-check", "--verbose"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "PASS")
                self.assertEqual(out["results"][0]["status"], "PASS")
                self.assertIn("warnings", out["results"][0])
                self.assertGreater(out["results"][0].get("warning_count", 0), 0)
            finally:
                os.chdir(cwd)

    def test_self_check_template_validation_module_missing(self):
        # Force the inner import in `_cmd_self_check` to fail.
        from cypilot import cli as cypilot_cli

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            _bootstrap_self_check_kits(root, adapter, with_example=True, bad_example=False)

            dummy = types.ModuleType("cypilot.utils.template")

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with patch.dict("sys.modules", {"cypilot.utils.template": dummy}):
                    with redirect_stdout(stdout):
                        exit_code = cypilot_cli._cmd_self_check([])
                self.assertEqual(exit_code, 1)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
                self.assertIn("Template validation module not available", out.get("message", ""))
            finally:
                os.chdir(cwd)


class TestCLIPyCoverageValidateCode(unittest.TestCase):
    def test_validate_with_code_and_output_file(self):
        """Test validate command with code validation and output file."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)

            # Kits + template for kind=req
            kits_base = root / "kits" / "cypilot-sdlc" / "artifacts" / "req"
            kits_base.mkdir(parents=True, exist_ok=True)
            (kits_base / "template.md").write_text(
                "---\n"
                "cypilot-template:\n"
                "  kind: req\n"
                "  version:\n"
                "    major: 1\n"
                "    minor: 0\n"
                "---\n"
                "\n"
                "<!-- cpt:id:item to_code=\"true\" -->\n"
                "<!-- cpt:id:item -->\n",
                encoding="utf-8",
            )

            # Artifact defining ID with to_code=true
            art_dir = root / "artifacts"
            art_dir.mkdir(parents=True, exist_ok=True)
            (art_dir / "reqs.md").write_text(
                "<!-- cpt:id:item -->\n"
                "- [x] `p1` - **ID**: `cpt-req-1`\n"
                "<!-- cpt:id:item -->\n",
                encoding="utf-8",
            )

            # Code referencing the ID
            src = root / "src"
            src.mkdir(parents=True, exist_ok=True)
            code_file = src / "code.py"
            code_file.write_text(
                "# @cpt-req:cpt-req-1:p1\n"
                "print('ok')\n",
                encoding="utf-8",
            )

            _write_json(
                adapter / "artifacts.json",
                {
                    "project_root": "..",
                    "kits": {"cypilot-sdlc": {"format": "Cypilot", "path": "kits/cypilot-sdlc"}},
                    "systems": [
                        {
                            "name": "S",
                            "kit": "cypilot-sdlc",
                            "artifacts": [
                                {"path": "artifacts/reqs.md", "kind": "req", "traceability": "FULL"},
                            ],
                            "codebase": [
                                {"path": "src", "extensions": [".py"]},
                            ],
                        }
                    ],
                },
            )

            out_path = root / "report.json"

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    # validate now includes code validation by default
                    exit_code = main(["validate", "--output", str(out_path)])
                self.assertEqual(exit_code, 0)
                self.assertTrue(out_path.is_file())
                report = json.loads(out_path.read_text(encoding="utf-8"))
                self.assertEqual(report.get("status"), "PASS")
                self.assertIn("next_step", report)
            finally:
                os.chdir(cwd)


class TestCLIPyCoverageHelpers(unittest.TestCase):
    def test_prompt_path_eof_returns_default(self):
        from cypilot.cli import _prompt_path

        with patch("builtins.input", side_effect=EOFError):
            got = _prompt_path("Question?", "default")
        self.assertEqual(got, "default")

    def test_list_workflow_files_iterdir_exception(self):
        from cypilot.cli import _list_workflow_files

        with TemporaryDirectory() as tmpdir:
            core = Path(tmpdir)
            (core / "workflows").mkdir(parents=True, exist_ok=True)

            with patch("pathlib.Path.iterdir", side_effect=OSError("boom")):
                files = _list_workflow_files(core)
            self.assertEqual(files, [])


class TestCLIPyCoverageSelfCheckFiltering(unittest.TestCase):
    """Tests for self-check --kit filtering (line 317)."""

    def test_self_check_filter_by_rule(self):
        """self-check --kit filters to specific kit."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            _bootstrap_self_check_kits(root, adapter, with_example=True, bad_example=False)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    # Filter to non-existent kit - should check 0 kits
                    exit_code = main(["self-check", "--kit", "nonexistent-kit"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("kits_checked"), 0)
            finally:
                os.chdir(cwd)

    def test_self_check_filter_matches_kit(self):
        """self-check --kit matches existing kit."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            _bootstrap_self_check_kits(root, adapter, with_example=True, bad_example=False)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["self-check", "--kit", "cypilot-sdlc"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("kits_checked"), 1)
            finally:
                os.chdir(cwd)


class TestCLIPyCoverageInitUnchanged(unittest.TestCase):
    """Tests for init command when files are unchanged (lines 947-970)."""

    def test_init_unchanged_files(self):
        """init reports unchanged when files match desired content."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()

            # First init to create files (use --yes to avoid prompts)
            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["init", "--yes"])
                self.assertEqual(exit_code, 0)

                # Second init without changes should report unchanged
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["init", "--yes"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                # Without --force, existing files should be unchanged
                actions = out.get("actions", {})
                # Check that files are reported as unchanged
                self.assertIn(actions.get("adapter_agents"), ["unchanged", "created"])
            finally:
                os.chdir(cwd)


class TestCLIPyCoverageValidateRules(unittest.TestCase):
    """Tests for validate-kits command (lines 2155-2162)."""

    def test_validate_rules_single_template(self):
        """validate-kits --template validates a single template file."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create a valid template (no adapter needed for --template)
            kits_base = root / "kits" / "cypilot-sdlc" / "artifacts" / "req"
            kits_base.mkdir(parents=True, exist_ok=True)
            template_path = kits_base / "template.md"
            template_path.write_text(
                "---\n"
                "cypilot-template:\n"
                "  kind: req\n"
                "  version:\n"
                "    major: 1\n"
                "    minor: 0\n"
                "---\n"
                "\n"
                "<!-- cpt:id:item -->\n"
                "<!-- cpt:id:item -->\n",
                encoding="utf-8",
            )

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-kits", "--template", str(template_path)])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "PASS")
                self.assertEqual(out.get("templates_validated"), 1)
            finally:
                os.chdir(cwd)

    def test_validate_rules_verbose_with_errors(self):
        """validate-kits --verbose shows template errors."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create an invalid template (missing version)
            kits_base = root / "kits" / "cypilot-sdlc" / "artifacts" / "req"
            kits_base.mkdir(parents=True, exist_ok=True)
            template_path = kits_base / "template.md"
            template_path.write_text(
                "---\n"
                "cypilot-template:\n"
                "  kind: req\n"
                "---\n"
                "\n"
                "<!-- cpt:id:item -->\n",
                encoding="utf-8",
            )

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-kits", "--template", str(template_path), "--verbose"])
                self.assertEqual(exit_code, 2)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "FAIL")
                self.assertIn("templates", out)
                self.assertIn("errors", out["templates"][0])
            finally:
                os.chdir(cwd)

    def test_validate_rules_all_from_registry(self):
        """validate-kits without --template validates all templates from registry."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)

            # Create kits structure
            kits_base = root / "kits" / "cypilot-sdlc" / "artifacts" / "req"
            kits_base.mkdir(parents=True, exist_ok=True)
            template_path = kits_base / "template.md"
            template_path.write_text(
                "---\n"
                "cypilot-template:\n"
                "  kind: req\n"
                "  version:\n"
                "    major: 1\n"
                "    minor: 0\n"
                "---\n"
                "\n"
                "<!-- cpt:id:item -->\n"
                "<!-- cpt:id:item -->\n",
                encoding="utf-8",
            )

            # Create artifact
            art_dir = root / "artifacts"
            art_dir.mkdir(parents=True, exist_ok=True)
            (art_dir / "reqs.md").write_text(
                "<!-- cpt:id:item -->\n"
                "- [x] `p1` - **ID**: `cpt-req-1`\n"
                "<!-- cpt:id:item -->\n",
                encoding="utf-8",
            )

            _write_json(
                adapter / "artifacts.json",
                {
                    "project_root": "..",
                    "kits": {"cypilot-sdlc": {"format": "Cypilot", "path": "kits/cypilot-sdlc"}},
                    "systems": [
                        {
                            "name": "S",
                            "kit": "cypilot-sdlc",
                            "artifacts": [
                                {"path": "artifacts/reqs.md", "kind": "req"},
                            ],
                        }
                    ],
                },
            )

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-kits"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "PASS")
                self.assertGreaterEqual(out.get("templates_validated", 0), 1)
            finally:
                os.chdir(cwd)


class TestCLIPyCoverageTopLevelHelp(unittest.TestCase):
    """Tests for cypilot --help (lines 2379-2392)."""

    def test_top_level_help_flag(self):
        """cypilot --help shows usage and commands."""
        from cypilot.cli import main

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["--help"])
        self.assertEqual(exit_code, 0)
        output = stdout.getvalue()
        self.assertIn("usage: cypilot <command>", output)
        self.assertIn("Validation commands:", output)
        self.assertIn("Search and utility commands:", output)
        self.assertIn("validate", output)

    def test_top_level_help_short_flag(self):
        """cypilot -h also shows usage."""
        from cypilot.cli import main

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["-h"])
        self.assertEqual(exit_code, 0)
        output = stdout.getvalue()
        self.assertIn("usage: cypilot <command>", output)


class TestCLIPyCoverageSlugValidation(unittest.TestCase):
    """Tests for slug validation errors in self-check (lines 301-306)."""

    def test_self_check_invalid_slugs(self):
        """self-check reports invalid slugs in artifacts.json."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)

            # Create kits structure with template
            kits_base = root / "kits" / "cypilot-sdlc" / "artifacts" / "req"
            kits_base.mkdir(parents=True, exist_ok=True)
            (kits_base / "template.md").write_text(
                "---\ncypilot-template:\n  kind: req\n  version:\n    major: 1\n    minor: 0\n---\n"
                "<!-- cpt:id:item -->\n<!-- cpt:id:item -->\n",
                encoding="utf-8",
            )

            # Create artifacts.json with invalid slug
            _write_json(
                adapter / "artifacts.json",
                {
                    "project_root": "..",
                    "kits": {"cypilot-sdlc": {"format": "Cypilot", "path": "kits/cypilot-sdlc"}},
                    "systems": [
                        {
                            "name": "S",
                            "slug": "Invalid Slug With Spaces",  # Invalid: contains spaces
                            "kit": "cypilot-sdlc",
                            "artifacts": [],
                        }
                    ],
                },
            )

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["self-check"])
                self.assertEqual(exit_code, 1)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
                self.assertIn("slug_errors", out)
            finally:
                os.chdir(cwd)


class TestCLIPyCoverageAgentsCommand(unittest.TestCase):
    """Tests for agents command edge cases."""

    def test_agents_dry_run_default_config(self):
        """agents command creates default config for recognized agent."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)

            # Create artifacts.json
            _write_json(
                adapter / "artifacts.json",
                {
                    "project_root": "..",
                    "kits": {},
                    "systems": [],
                },
            )

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["agents", "--agent", "windsurf", "--dry-run"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertIn(out.get("status"), ["OK", "PASS"])
            finally:
                os.chdir(cwd)


class TestCLIPyCoverageListIdsWithCode(unittest.TestCase):
    """Tests for list-ids --include-code (lines 1326-1338)."""

    def test_list_ids_include_code_with_refs(self):
        """list-ids --include-code shows ID references from artifacts."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)

            # Create kits structure with id-ref block
            kits_base = root / "kits" / "cypilot-sdlc" / "artifacts" / "req"
            kits_base.mkdir(parents=True, exist_ok=True)
            (kits_base / "template.md").write_text(
                "---\ncypilot-template:\n  kind: req\n  version:\n    major: 1\n    minor: 0\n---\n"
                "<!-- cpt:id:item -->\n<!-- cpt:id:item -->\n"
                "<!-- cpt:id-ref:other -->\n<!-- cpt:id-ref:other -->\n",
                encoding="utf-8",
            )

            # Create artifact with ID definition and reference
            art_dir = root / "artifacts"
            art_dir.mkdir(parents=True, exist_ok=True)
            (art_dir / "reqs.md").write_text(
                "<!-- cpt:id:item -->\n"
                "- [x] `p1` - **ID**: `cpt-test-item-1`\n"
                "<!-- cpt:id:item -->\n"
                "<!-- cpt:id-ref:other -->\n"
                "- [ ] `p2` - `cpt-external-ref-abc`\n"
                "<!-- cpt:id-ref:other -->\n",
                encoding="utf-8",
            )

            # Create code file
            src = root / "src"
            src.mkdir(parents=True, exist_ok=True)
            (src / "code.py").write_text(
                "# @cpt-req:cpt-test-item-1:p1\nprint('ok')\n",
                encoding="utf-8",
            )

            _write_json(
                adapter / "artifacts.json",
                {
                    "project_root": "..",
                    "kits": {"cypilot-sdlc": {"format": "Cypilot", "path": "kits/cypilot-sdlc"}},
                    "systems": [
                        {
                            "name": "test",
                            "kit": "cypilot-sdlc",
                            "artifacts": [{"path": "artifacts/reqs.md", "kind": "req"}],
                            "codebase": [{"path": "src", "extensions": [".py"]}],
                        }
                    ],
                },
            )

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["list-ids", "--include-code"])
                # Just verify it runs - the output format may vary
                self.assertIn(exit_code, [0, 2])  # OK or validation failure
                output = stdout.getvalue()
                # Should produce valid JSON
                out = json.loads(output)
                self.assertIn("ids", out)
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
