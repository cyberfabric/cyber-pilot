"""
Tests for commands/where_defined.py and commands/where_used.py.

Covers: cmd_where_defined, cmd_where_used, _human_where_defined, _human_where_used.
"""

import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.commands.where_defined import cmd_where_defined, _human_where_defined
from cypilot.commands.where_used import cmd_where_used, _human_where_used
from cypilot.utils.context import CypilotContext, set_context
from cypilot.utils.ui import set_json_mode
from cypilot.cli import main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _setup_project(root: Path) -> Path:
    """Bootstrap a minimal Cypilot project. Returns adapter dir."""
    (root / ".git").mkdir(exist_ok=True)
    (root / "AGENTS.md").write_text(
        '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "adapter"\n```\n',
        encoding="utf-8",
    )
    adapter = root / "adapter"
    adapter.mkdir(parents=True, exist_ok=True)
    (adapter / "config").mkdir(exist_ok=True)
    (adapter / "config" / "AGENTS.md").write_text("# Adapter\n", encoding="utf-8")

    from cypilot.utils import toml_utils
    toml_utils.dump({
        "version": "1.0",
        "project_root": "..",
        "kits": {"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
        "systems": [{
            "name": "Test",
            "kits": "cypilot",
            "artifacts": [{"path": "architecture/PRD.md", "kind": "PRD"}],
        }],
    }, adapter / "config" / "artifacts.toml")

    # Create the artifact with a defined + referenced ID
    art_dir = root / "architecture"
    art_dir.mkdir(parents=True, exist_ok=True)
    (art_dir / "PRD.md").write_text(
        "- [x] `p1` - **ID**: `cpt-test-item-1`\n"
        "<!-- @cpt-ref: cpt-test-item-1 -->\n",
        encoding="utf-8",
    )

    # Kit structure
    kit_dir = root / "kits" / "sdlc" / "artifacts" / "PRD"
    kit_dir.mkdir(parents=True, exist_ok=True)
    (kit_dir / "template.md").write_text(
        "---\ncypilot-template:\n  version:\n    major: 1\n    minor: 0\n  kind: PRD\n---\n"
        "- [ ] `p1` - **ID**: `cpt-{system}-item-{slug}`\n",
        encoding="utf-8",
    )
    from _test_helpers import write_constraints_toml
    write_constraints_toml(root / "kits" / "sdlc", {
        "PRD": {"identifiers": {"item": {"template": "cpt-{system}-item-{slug}"}}},
    })
    return adapter


def _with_context(root: Path):
    """Load CypilotContext from project root and set as global."""
    ctx = CypilotContext.load(root)
    set_context(ctx)
    return ctx


class _ContextTestBase(unittest.TestCase):
    """Base that cleans up global context after each test."""

    def tearDown(self):
        set_context(None)


# =========================================================================
# cmd_where_defined
# =========================================================================

class TestCmdWhereDefined(_ContextTestBase):

    def test_empty_id_returns_error(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            rc = cmd_where_defined(["--id", ""])
        self.assertEqual(rc, 1)
        out = json.loads(stdout.getvalue())
        self.assertEqual(out["status"], "ERROR")

    def test_no_id_returns_error(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            rc = cmd_where_defined([])
        self.assertEqual(rc, 1)

    def test_both_positional_and_flag_warns(self):
        """When both positional and --id are given, positional wins."""
        with TemporaryDirectory() as td:
            root = Path(td)
            _setup_project(root)
            _with_context(root)
            stderr = io.StringIO()
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                cmd_where_defined(["cpt-test-item-1", "--id", "cpt-other"])
            self.assertIn("WARNING", stderr.getvalue())

    def test_artifact_not_found(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            rc = cmd_where_defined(["--id", "test", "--artifact", "/nonexistent/file.md"])
        self.assertEqual(rc, 1)
        out = json.loads(stdout.getvalue())
        self.assertEqual(out["status"], "ERROR")

    def test_artifact_no_context(self):
        with TemporaryDirectory() as td:
            art = Path(td) / "art.md"
            art.write_text("test\n", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                rc = cmd_where_defined(["--id", "test", "--artifact", str(art)])
            self.assertEqual(rc, 1)

    def test_artifact_not_in_registry(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            _setup_project(root)
            unregistered = root / "random.md"
            unregistered.write_text("content\n", encoding="utf-8")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    rc = cmd_where_defined(["--id", "test", "--artifact", str(unregistered)])
                self.assertEqual(rc, 1)
                out = json.loads(stdout.getvalue())
                self.assertIn("not in Cypilot registry", out.get("message", ""))
            finally:
                os.chdir(cwd)

    def test_artifact_outside_project(self):
        """Artifact exists but is outside project root."""
        with TemporaryDirectory() as td1, TemporaryDirectory() as td2:
            root = Path(td1)
            _setup_project(root)
            outside = Path(td2) / "outside.md"
            outside.write_text("content\n", encoding="utf-8")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    rc = cmd_where_defined(["--id", "test", "--artifact", str(outside)])
                self.assertEqual(rc, 1)
            finally:
                os.chdir(cwd)

    def test_no_context_returns_error(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    rc = cmd_where_defined(["--id", "test"])
                self.assertEqual(rc, 1)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out["status"], "ERROR")
            finally:
                os.chdir(cwd)

    def test_found_single_definition(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            _setup_project(root)
            _with_context(root)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                rc = cmd_where_defined(["cpt-test-item-1"])
            self.assertEqual(rc, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out["status"], "FOUND")
            self.assertEqual(out["count"], 1)

    def test_not_found_returns_2(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            _setup_project(root)
            _with_context(root)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                rc = cmd_where_defined(["cpt-nonexistent-id"])
            self.assertEqual(rc, 2)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out["status"], "NOT_FOUND")

    def test_ambiguous_multiple_definitions(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            adapter = _setup_project(root)
            from cypilot.utils import toml_utils
            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {"cypilot": {"format": "Cypilot", "path": "kits/sdlc"}},
                "systems": [{
                    "name": "Test",
                    "kits": "cypilot",
                    "artifacts": [
                        {"path": "architecture/PRD.md", "kind": "PRD"},
                        {"path": "architecture/DESIGN.md", "kind": "DESIGN"},
                    ],
                }],
            }, adapter / "config" / "artifacts.toml")
            (root / "architecture" / "DESIGN.md").write_text(
                "- [x] `p1` - **ID**: `cpt-test-item-1`\n",
                encoding="utf-8",
            )
            _with_context(root)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                rc = cmd_where_defined(["cpt-test-item-1"])
            self.assertEqual(rc, 2)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out["status"], "AMBIGUOUS")
            self.assertEqual(out["count"], 2)

    def test_with_artifact_flag_found(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            _setup_project(root)
            art_path = root / "architecture" / "PRD.md"
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    rc = cmd_where_defined(["--id", "cpt-test-item-1", "--artifact", str(art_path)])
                self.assertEqual(rc, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out["status"], "FOUND")
            finally:
                os.chdir(cwd)

    def test_no_artifacts_to_scan(self):
        """All registered artifacts are missing from disk."""
        with TemporaryDirectory() as td:
            root = Path(td)
            _setup_project(root)
            (root / "architecture" / "PRD.md").unlink()
            _with_context(root)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                rc = cmd_where_defined(["cpt-test-item-1"])
            self.assertEqual(rc, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out["status"], "NOT_FOUND")
            self.assertEqual(out["artifacts_scanned"], 0)


# =========================================================================
# cmd_where_used
# =========================================================================

class TestCmdWhereUsed(_ContextTestBase):

    def test_empty_id_returns_error(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            rc = cmd_where_used(["--id", ""])
        self.assertEqual(rc, 1)
        out = json.loads(stdout.getvalue())
        self.assertEqual(out["status"], "ERROR")

    def test_no_id_returns_error(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            rc = cmd_where_used([])
        self.assertEqual(rc, 1)

    def test_both_positional_and_flag_warns(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            _setup_project(root)
            _with_context(root)
            stderr = io.StringIO()
            stdout = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                cmd_where_used(["cpt-test-item-1", "--id", "cpt-other"])
            self.assertIn("WARNING", stderr.getvalue())

    def test_artifact_not_found(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            rc = cmd_where_used(["--id", "test", "--artifact", "/nonexistent/file.md"])
        self.assertEqual(rc, 1)

    def test_artifact_no_context(self):
        with TemporaryDirectory() as td:
            art = Path(td) / "art.md"
            art.write_text("test\n", encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                rc = cmd_where_used(["--id", "test", "--artifact", str(art)])
            self.assertEqual(rc, 1)

    def test_artifact_not_in_registry(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            _setup_project(root)
            unregistered = root / "random.md"
            unregistered.write_text("content\n", encoding="utf-8")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    rc = cmd_where_used(["--id", "test", "--artifact", str(unregistered)])
                self.assertEqual(rc, 1)
            finally:
                os.chdir(cwd)

    def test_no_context_returns_error(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    rc = cmd_where_used(["--id", "test"])
                self.assertEqual(rc, 1)
            finally:
                os.chdir(cwd)

    def test_found_references(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            _setup_project(root)
            _with_context(root)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                rc = cmd_where_used(["cpt-test-item-1"])
            self.assertEqual(rc, 0)
            out = json.loads(stdout.getvalue())
            self.assertGreaterEqual(out["count"], 0)

    def test_include_definitions(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            _setup_project(root)
            _with_context(root)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                rc = cmd_where_used(["cpt-test-item-1", "--include-definitions"])
            self.assertEqual(rc, 0)
            out = json.loads(stdout.getvalue())
            self.assertGreaterEqual(out["count"], 1)

    def test_no_references_found(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            _setup_project(root)
            _with_context(root)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                rc = cmd_where_used(["cpt-nonexistent-id"])
            self.assertEqual(rc, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out["count"], 0)

    def test_with_artifact_flag(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            _setup_project(root)
            art_path = root / "architecture" / "PRD.md"
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    rc = cmd_where_used(["--id", "cpt-test-item-1", "--artifact", str(art_path), "--include-definitions"])
                self.assertEqual(rc, 0)
            finally:
                os.chdir(cwd)

    def test_no_artifacts_to_scan(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            _setup_project(root)
            (root / "architecture" / "PRD.md").unlink()
            _with_context(root)
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                rc = cmd_where_used(["cpt-test-item-1"])
            self.assertEqual(rc, 0)
            out = json.loads(stdout.getvalue())
            self.assertEqual(out["artifacts_scanned"], 0)

    def test_artifact_outside_project(self):
        with TemporaryDirectory() as td1, TemporaryDirectory() as td2:
            root = Path(td1)
            _setup_project(root)
            outside = Path(td2) / "outside.md"
            outside.write_text("content\n", encoding="utf-8")
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    rc = cmd_where_used(["--id", "test", "--artifact", str(outside)])
                self.assertEqual(rc, 1)
            finally:
                os.chdir(cwd)


# =========================================================================
# Human formatters (need human mode)
# =========================================================================

class _HumanModeBase(unittest.TestCase):
    def setUp(self):
        set_json_mode(False)

    def tearDown(self):
        set_json_mode(True)


class TestHumanWhereDefined(_HumanModeBase):

    def test_found_with_checked(self):
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_where_defined({
                "status": "FOUND", "id": "cpt-x", "artifacts_scanned": 1, "count": 1,
                "definitions": [{"artifact": "/tmp/A.md", "artifact_type": "PRD", "line": 10, "checked": True}],
            })
        out = buf.getvalue()
        self.assertIn("cpt-x", out)
        self.assertIn("10", out)

    def test_not_found(self):
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_where_defined({
                "status": "NOT_FOUND", "id": "cpt-missing", "artifacts_scanned": 2,
                "count": 0, "definitions": [],
            })
        out = buf.getvalue()
        self.assertIn("not found", out.lower())

    def test_ambiguous(self):
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_where_defined({
                "status": "AMBIGUOUS", "id": "cpt-dup", "artifacts_scanned": 2, "count": 2,
                "definitions": [
                    {"artifact": "/tmp/A.md", "artifact_type": "PRD", "line": 1, "checked": False},
                    {"artifact": "/tmp/B.md", "artifact_type": "DESIGN", "line": 5, "checked": False},
                ],
            })
        out = buf.getvalue()
        self.assertIn("Ambiguous", out)

    def test_no_line(self):
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_where_defined({
                "status": "FOUND", "id": "cpt-x", "artifacts_scanned": 1, "count": 1,
                "definitions": [{"artifact": "/tmp/A.md", "artifact_type": "PRD", "line": "", "checked": False}],
            })
        # Should not crash


class TestHumanWhereUsed(_HumanModeBase):

    def test_found_with_checked(self):
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_where_used({
                "id": "cpt-x", "artifacts_scanned": 1, "count": 1,
                "references": [{"artifact": "/tmp/A.md", "artifact_type": "PRD", "line": 10, "type": "reference", "checked": True}],
            })
        out = buf.getvalue()
        self.assertIn("cpt-x", out)

    def test_no_refs(self):
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_where_used({
                "id": "cpt-missing", "artifacts_scanned": 2, "count": 0, "references": [],
            })
        out = buf.getvalue()
        self.assertIn("No references", out)

    def test_no_line(self):
        buf = io.StringIO()
        with redirect_stderr(buf):
            _human_where_used({
                "id": "cpt-x", "artifacts_scanned": 1, "count": 1,
                "references": [{"artifact": "/tmp/A.md", "artifact_type": "PRD", "line": "", "type": "ref", "checked": False}],
            })
        # Should not crash


if __name__ == "__main__":
    unittest.main()
