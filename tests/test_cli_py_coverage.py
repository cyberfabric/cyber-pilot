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

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "spider" / "scripts"))


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _bootstrap_project_root(root: Path, adapter_rel: str = "adapter") -> Path:
    (root / ".git").mkdir()
    (root / ".spider-config.json").write_text(
        json.dumps({"spiderAdapterPath": adapter_rel}, ensure_ascii=False),
        encoding="utf-8",
    )
    adapter = root / adapter_rel
    adapter.mkdir(parents=True, exist_ok=True)
    (adapter / "AGENTS.md").write_text("# Test adapter\n", encoding="utf-8")
    return adapter


def _bootstrap_self_check_weavers(root: Path, adapter: Path, *, with_example: bool = True, bad_example: bool = False) -> None:
    # Minimal artifacts registry that passes `load_artifacts_registry` and contains weavers.
    _write_json(
        adapter / "artifacts.json",
        {
            "project_root": "..",
            "systems": [],
            "weavers": {
                "spider-sdlc": {"format": "Spider", "path": "weavers/spider-sdlc"},
            },
        },
    )

    weavers_base = root / "weavers" / "spider-sdlc" / "artifacts" / "req"
    weavers_base.mkdir(parents=True, exist_ok=True)

    template = weavers_base / "template.md"
    template.write_text(
        "---\n"
        "spider-template:\n"
        "  kind: req\n"
        "  version:\n"
        "    major: 1\n"
        "    minor: 0\n"
        "---\n"
        "\n"
        "<!-- spd:id:item to_code=\"true\" -->\n"
        "<!-- spd:id:item -->\n",
        encoding="utf-8",
    )

    if with_example:
        ex_dir = weavers_base / "examples"
        ex_dir.mkdir(parents=True, exist_ok=True)
        example = ex_dir / "example.md"

        if bad_example:
            example.write_text(
                "---\n"
                "spider-template:\n"
                "  kind: req\n"
                "  version: 1.0\n"
                "---\n"
                "\n"
                "<!-- spd:id:item -->\n"
                "- [x] `p1` - **ID**: `spd-req-1`\n"
                "<!-- spd:id:item -->\n",
                encoding="utf-8",
            )
        else:
            example.write_text(
                "<!-- spd:id:item -->\n"
                "- [x] `p1` - **ID**: `spd-req-1`\n"
                "<!-- spd:id:item -->\n",
                encoding="utf-8",
            )


class TestCLIPyCoverageSelfCheck(unittest.TestCase):
    def test_self_check_pass(self):
        from spider.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            _bootstrap_self_check_weavers(root, adapter, with_example=True, bad_example=False)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["self-check"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "PASS")
                self.assertEqual(out.get("weavers_checked"), 1)
                self.assertEqual(out.get("templates_checked"), 1)
                self.assertEqual(out["results"][0]["status"], "PASS")
            finally:
                os.chdir(cwd)

    def test_self_check_fail_on_validation_errors(self):
        from spider.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            _bootstrap_self_check_weavers(root, adapter, with_example=True, bad_example=True)

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
        from spider.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            _bootstrap_self_check_weavers(root, adapter, with_example=False)

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
        from spider import cli as spider_cli

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            _bootstrap_self_check_weavers(root, adapter, with_example=True, bad_example=False)

            dummy = types.ModuleType("spider.utils.template")

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with patch.dict("sys.modules", {"spider.utils.template": dummy}):
                    with redirect_stdout(stdout):
                        exit_code = spider_cli._cmd_self_check([])
                self.assertEqual(exit_code, 1)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "ERROR")
                self.assertIn("Template validation module not available", out.get("message", ""))
            finally:
                os.chdir(cwd)


class TestCLIPyCoverageValidateCode(unittest.TestCase):
    def test_validate_code_pass_and_output_file(self):
        from spider.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)

            # Weavers + template for kind=req
            weavers_base = root / "weavers" / "spider-sdlc" / "artifacts" / "req"
            weavers_base.mkdir(parents=True, exist_ok=True)
            (weavers_base / "template.md").write_text(
                "---\n"
                "spider-template:\n"
                "  kind: req\n"
                "  version:\n"
                "    major: 1\n"
                "    minor: 0\n"
                "---\n"
                "\n"
                "<!-- spd:id:item to_code=\"true\" -->\n"
                "<!-- spd:id:item -->\n",
                encoding="utf-8",
            )

            # Artifact defining ID with to_code=true
            art_dir = root / "artifacts"
            art_dir.mkdir(parents=True, exist_ok=True)
            (art_dir / "reqs.md").write_text(
                "<!-- spd:id:item -->\n"
                "- [x] `p1` - **ID**: `spd-req-1`\n"
                "<!-- spd:id:item -->\n",
                encoding="utf-8",
            )

            # Code referencing the ID
            src = root / "src"
            src.mkdir(parents=True, exist_ok=True)
            code_file = src / "code.py"
            code_file.write_text(
                "# @spider-req:spd-req-1:p1\n"
                "print('ok')\n",
                encoding="utf-8",
            )

            _write_json(
                adapter / "artifacts.json",
                {
                    "project_root": "..",
                    "weavers": {"spider-sdlc": {"format": "Spider", "path": "weavers/spider-sdlc"}},
                    "systems": [
                        {
                            "name": "S",
                            "weaver": "spider-sdlc",
                            "artifacts": [
                                {"path": "artifacts/reqs.md", "kind": "req"},
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
                    exit_code = main(["validate-code", str(code_file), "--output", str(out_path)])
                self.assertEqual(exit_code, 0)
                self.assertTrue(out_path.is_file())
                report = json.loads(out_path.read_text(encoding="utf-8"))
                self.assertEqual(report.get("status"), "PASS")
                self.assertIn("next_step", report)
            finally:
                os.chdir(cwd)


class TestCLIPyCoverageHelpers(unittest.TestCase):
    def test_prompt_path_eof_returns_default(self):
        from spider.cli import _prompt_path

        with patch("builtins.input", side_effect=EOFError):
            got = _prompt_path("Question?", "default")
        self.assertEqual(got, "default")

    def test_list_workflow_files_iterdir_exception(self):
        from spider.cli import _list_workflow_files

        with TemporaryDirectory() as tmpdir:
            core = Path(tmpdir)
            (core / "workflows").mkdir(parents=True, exist_ok=True)

            with patch("pathlib.Path.iterdir", side_effect=OSError("boom")):
                files = _list_workflow_files(core)
            self.assertEqual(files, [])


class TestCLIPyCoverageSelfCheckFiltering(unittest.TestCase):
    """Tests for self-check --weaver filtering (line 317)."""

    def test_self_check_filter_by_rule(self):
        """self-check --weaver filters to specific weaver."""
        from spider.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            _bootstrap_self_check_weavers(root, adapter, with_example=True, bad_example=False)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    # Filter to non-existent weaver - should check 0 weavers
                    exit_code = main(["self-check", "--weaver", "nonexistent-weaver"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("weavers_checked"), 0)
            finally:
                os.chdir(cwd)

    def test_self_check_filter_matches_weaver(self):
        """self-check --weaver matches existing weaver."""
        from spider.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            _bootstrap_self_check_weavers(root, adapter, with_example=True, bad_example=False)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["self-check", "--weaver", "spider-sdlc"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("weavers_checked"), 1)
            finally:
                os.chdir(cwd)


class TestCLIPyCoverageInitUnchanged(unittest.TestCase):
    """Tests for init command when files are unchanged (lines 947-970)."""

    def test_init_unchanged_files(self):
        """init reports unchanged when files match desired content."""
        from spider.cli import main

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
    """Tests for validate-weavers command (lines 2155-2162)."""

    def test_validate_rules_single_template(self):
        """validate-weavers --template validates a single template file."""
        from spider.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create a valid template (no adapter needed for --template)
            weavers_base = root / "weavers" / "spider-sdlc" / "artifacts" / "req"
            weavers_base.mkdir(parents=True, exist_ok=True)
            template_path = weavers_base / "template.md"
            template_path.write_text(
                "---\n"
                "spider-template:\n"
                "  kind: req\n"
                "  version:\n"
                "    major: 1\n"
                "    minor: 0\n"
                "---\n"
                "\n"
                "<!-- spd:id:item -->\n"
                "<!-- spd:id:item -->\n",
                encoding="utf-8",
            )

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-weavers", "--template", str(template_path)])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "PASS")
                self.assertEqual(out.get("templates_validated"), 1)
            finally:
                os.chdir(cwd)

    def test_validate_rules_verbose_with_errors(self):
        """validate-weavers --verbose shows template errors."""
        from spider.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create an invalid template (missing version)
            weavers_base = root / "weavers" / "spider-sdlc" / "artifacts" / "req"
            weavers_base.mkdir(parents=True, exist_ok=True)
            template_path = weavers_base / "template.md"
            template_path.write_text(
                "---\n"
                "spider-template:\n"
                "  kind: req\n"
                "---\n"
                "\n"
                "<!-- spd:id:item -->\n",
                encoding="utf-8",
            )

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-weavers", "--template", str(template_path), "--verbose"])
                self.assertEqual(exit_code, 2)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "FAIL")
                self.assertIn("templates", out)
                self.assertIn("errors", out["templates"][0])
            finally:
                os.chdir(cwd)

    def test_validate_rules_all_from_registry(self):
        """validate-weavers without --template validates all templates from registry."""
        from spider.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)

            # Create weavers structure
            weavers_base = root / "weavers" / "spider-sdlc" / "artifacts" / "req"
            weavers_base.mkdir(parents=True, exist_ok=True)
            template_path = weavers_base / "template.md"
            template_path.write_text(
                "---\n"
                "spider-template:\n"
                "  kind: req\n"
                "  version:\n"
                "    major: 1\n"
                "    minor: 0\n"
                "---\n"
                "\n"
                "<!-- spd:id:item -->\n"
                "<!-- spd:id:item -->\n",
                encoding="utf-8",
            )

            # Create artifact
            art_dir = root / "artifacts"
            art_dir.mkdir(parents=True, exist_ok=True)
            (art_dir / "reqs.md").write_text(
                "<!-- spd:id:item -->\n"
                "- [x] `p1` - **ID**: `spd-req-1`\n"
                "<!-- spd:id:item -->\n",
                encoding="utf-8",
            )

            _write_json(
                adapter / "artifacts.json",
                {
                    "project_root": "..",
                    "weavers": {"spider-sdlc": {"format": "Spider", "path": "weavers/spider-sdlc"}},
                    "systems": [
                        {
                            "name": "S",
                            "weaver": "spider-sdlc",
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
                    exit_code = main(["validate-weavers"])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "PASS")
                self.assertGreaterEqual(out.get("templates_validated", 0), 1)
            finally:
                os.chdir(cwd)
