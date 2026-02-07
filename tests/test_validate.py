"""Tests for validation related utility functions.

NOTE: Tests for validation module (cascade, common, traceability, cdsl) were removed
because the validation module is not used by CLI commands and was deleted.
Only tests for CLI and utils functions are kept.
"""

import sys
import os
import json
from pathlib import Path
import io
import contextlib
import unittest
from tempfile import TemporaryDirectory


# Add skills/cypilot/scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.utils.files import (
    find_adapter_directory,
    find_project_root,
    load_artifacts_registry,
    load_project_config,
    load_text,
)

from cypilot import cli as cypilot_cli


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


class TestMain(unittest.TestCase):
    """Tests for main validation entry point."""
    def test_main_exit_code_fail(self):
        """Test that main() returns error code on validation failure."""
        with TemporaryDirectory() as td:
            root = Path(td)
            prd = root / "architecture" / "PRD.md"
            prd.parent.mkdir(parents=True, exist_ok=True)
            # Use disallowed link notation
            prd.write_text("# PRD\n\nSee @/some/path for details.\n", encoding="utf-8")

            _bootstrap_registry(
                root,
                entries=[
                    {"kind": "PRD", "system": "Test", "path": "architecture/PRD.md", "format": "Cypilot"},
                ],
            )

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = cypilot_cli.main([
                    "validate",
                    "--artifact",
                    str(prd),
                ])
            # validate returns 1 or 2 on error
            self.assertIn(code, [1, 2])


class TestParsingUtils(unittest.TestCase):
    """Tests for utils/parsing.py"""

    def test_parse_required_sections(self):
        from cypilot.utils.parsing import parse_required_sections
        with TemporaryDirectory() as td:
            req = Path(td) / "req.md"
            req.write_text("### Section A: Intro\n### Section B: Body\n", encoding="utf-8")
            result = parse_required_sections(req)
            self.assertEqual(result, {"A": "Intro", "B": "Body"})

    def test_split_by_section_letter_with_offsets(self):
        import re
        from cypilot.utils.parsing import split_by_section_letter_with_offsets
        section_re = re.compile(r"^##\s+([A-Z])\.\s+(.+)?$", re.IGNORECASE)
        text = "# Header\n\n## A. First\n\nContent A.\n\n## B. Second\n\nContent B.\n"
        order, sections, offsets = split_by_section_letter_with_offsets(text, section_re)
        self.assertEqual(order, ["A", "B"])
        self.assertIn("A", sections)
        self.assertIn("B", sections)
        self.assertIn("A", offsets)
        self.assertIn("B", offsets)



class TestFilesUtilsCoverage(unittest.TestCase):
    def test_find_project_root_none_when_no_markers(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            self.assertIsNone(find_project_root(root))

    def test_load_project_config_invalid_json_returns_none(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / ".cypilot-config.json").write_text("{bad", encoding="utf-8")
            self.assertIsNone(load_project_config(root))

    def test_find_adapter_directory_returns_none_when_config_path_invalid(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir(exist_ok=True)
            (root / ".cypilot-config.json").write_text('{"cypilotAdapterPath": "missing-adapter"}', encoding="utf-8")
            self.assertIsNone(find_adapter_directory(root))

    def test_load_artifacts_registry_error_branches(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            adapter = root / "adapter"
            adapter.mkdir(parents=True, exist_ok=True)

            reg, err = load_artifacts_registry(adapter)
            self.assertIsNone(reg)
            self.assertIsNotNone(err)

            (adapter / "artifacts.json").write_text("not-json", encoding="utf-8")
            reg, err = load_artifacts_registry(adapter)
            self.assertIsNone(reg)
            self.assertIsNotNone(err)

            (adapter / "artifacts.json").write_text(json.dumps([1, 2, 3]), encoding="utf-8")
            reg, err = load_artifacts_registry(adapter)
            self.assertIsNone(reg)
            self.assertIsNotNone(err)

            (adapter / "artifacts.json").write_text(json.dumps({"version": "1.0", "artifacts": []}), encoding="utf-8")
            reg, err = load_artifacts_registry(adapter)
            self.assertIsNotNone(reg)
            self.assertIsNone(err)

    def test_load_text_not_a_file(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            subdir = root / "subdir"
            subdir.mkdir()
            content, err = load_text(subdir)
            self.assertEqual(content, "")
            self.assertIsNotNone(err)


if __name__ == "__main__":
    unittest.main()
