"""
Focused unit tests for _inject_managed_block and its wrappers in commands/init.py.

Covers:
  A) Valid in-root write succeeds
  B) Sibling-prefix escape is rejected
  C) Clearly outside-root path is rejected
  D) _inject_root_agents / _inject_root_claude wrappers still work
"""

import io
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))


class TestInjectManagedBlockContainment(unittest.TestCase):
    """Path containment checks in _inject_managed_block."""

    def _fn(self):
        from cypilot.commands.init import _inject_managed_block
        return _inject_managed_block

    def test_valid_in_root_write_succeeds(self):
        """A: target directly inside project_root succeeds."""
        _inject_managed_block = self._fn()
        with TemporaryDirectory() as td:
            project_root = Path(td) / "project"
            project_root.mkdir()
            target = project_root / "AGENTS.md"
            result = _inject_managed_block(target, "cypilot", project_root=project_root)
            self.assertEqual(result, "created")
            self.assertTrue(target.is_file())

    def test_sibling_prefix_escape_is_rejected(self):
        """B: /tmp/project2/AGENTS.md must not be accepted as inside /tmp/project."""
        _inject_managed_block = self._fn()
        with TemporaryDirectory() as td:
            project_root = Path(td) / "project"
            project_root.mkdir()
            sibling = Path(td) / "project2"
            sibling.mkdir()
            target = sibling / "AGENTS.md"
            with self.assertRaises(ValueError) as ctx:
                _inject_managed_block(target, "cypilot", project_root=project_root)
            self.assertIn("Refusing to write outside project root", str(ctx.exception))

    def test_clearly_outside_root_is_rejected(self):
        """C: path in an unrelated directory must raise ValueError."""
        _inject_managed_block = self._fn()
        with TemporaryDirectory() as td:
            project_root = Path(td) / "project"
            project_root.mkdir()
            other = Path(td) / "other"
            other.mkdir()
            target = other / "AGENTS.md"
            with self.assertRaises(ValueError) as ctx:
                _inject_managed_block(target, "cypilot", project_root=project_root)
            self.assertIn("Refusing to write outside project root", str(ctx.exception))

    def test_no_project_root_skips_validation(self):
        """project_root=None disables the check entirely."""
        _inject_managed_block = self._fn()
        with TemporaryDirectory() as td:
            target = Path(td) / "anywhere" / "AGENTS.md"
            target.parent.mkdir()
            result = _inject_managed_block(target, "cypilot")
            self.assertEqual(result, "created")

    def test_nested_subdir_write_succeeds(self):
        """Target in a subdirectory under project_root is accepted."""
        _inject_managed_block = self._fn()
        with TemporaryDirectory() as td:
            project_root = Path(td) / "project"
            subdir = project_root / "subdir"
            subdir.mkdir(parents=True)
            target = subdir / "AGENTS.md"
            result = _inject_managed_block(target, "cypilot", project_root=project_root)
            self.assertEqual(result, "created")


class TestInjectRootWrappers(unittest.TestCase):
    """D: _inject_root_agents and _inject_root_claude still work correctly."""

    def test_inject_root_agents_creates(self):
        from cypilot.commands.init import _inject_root_agents
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            result = _inject_root_agents(root, "cypilot")
            self.assertEqual(result, "created")
            agents = root / "AGENTS.md"
            self.assertTrue(agents.is_file())
            self.assertIn('cypilot_path = "cypilot"', agents.read_text())

    def test_inject_root_agents_updates(self):
        from cypilot.commands.init import _inject_root_agents, MARKER_START, MARKER_END
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            agents = root / "AGENTS.md"
            agents.write_text(
                f"{MARKER_START}\n```toml\ncypilot_path = \"old\"\n```\n{MARKER_END}\n",
                encoding="utf-8",
            )
            result = _inject_root_agents(root, "newdir")
            self.assertEqual(result, "updated")
            self.assertIn('cypilot_path = "newdir"', agents.read_text())

    def test_inject_root_agents_unchanged(self):
        from cypilot.commands.init import _inject_root_agents, _compute_managed_block
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            agents = root / "AGENTS.md"
            agents.write_text(_compute_managed_block("cypilot") + "\n", encoding="utf-8")
            result = _inject_root_agents(root, "cypilot")
            self.assertEqual(result, "unchanged")

    def test_inject_root_claude_creates(self):
        from cypilot.commands.init import _inject_root_claude
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            result = _inject_root_claude(root, "cypilot")
            self.assertEqual(result, "created")
            claude = root / "CLAUDE.md"
            self.assertTrue(claude.is_file())
            self.assertIn('cypilot_path = "cypilot"', claude.read_text())

    def test_inject_root_claude_updates(self):
        from cypilot.commands.init import _inject_root_claude, MARKER_START, MARKER_END
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            claude = root / "CLAUDE.md"
            claude.write_text(
                f"{MARKER_START}\n```toml\ncypilot_path = \"old\"\n```\n{MARKER_END}\n",
                encoding="utf-8",
            )
            result = _inject_root_claude(root, "newdir")
            self.assertEqual(result, "updated")
            self.assertIn('cypilot_path = "newdir"', claude.read_text())

    def test_inject_root_agents_dry_run(self):
        from cypilot.commands.init import _inject_root_agents
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            result = _inject_root_agents(root, "cypilot", dry_run=True)
            self.assertEqual(result, "created")
            self.assertFalse((root / "AGENTS.md").exists())


class TestPromptKitInstallFlag(unittest.TestCase):
    """Coverage for _prompt_kit_install_flag interactive/non-interactive paths."""

    def _fn(self):
        from cypilot.commands.init import _prompt_kit_install_flag
        return _prompt_kit_install_flag

    def test_non_interactive_returns_true(self):
        """interactive=False: return True (--yes mode), no prompting."""
        self.assertTrue(self._fn()(False))

    def test_interactive_no_tty_returns_false(self):
        """interactive=True but stdin not a TTY: return False (not interactive)."""
        with patch("sys.stdin.isatty", return_value=False):
            self.assertFalse(self._fn()(True))

    def test_interactive_tty_accept(self):
        """User types 'a' → accepted; all six prompt lines written to stderr."""
        buf = io.StringIO()
        with patch("sys.stdin.isatty", return_value=True), \
             patch("sys.stderr", buf), \
             patch("builtins.input", return_value="a"):
            self.assertTrue(self._fn()(True))
        out = buf.getvalue()
        # Header + the four added help lines + the [a]ccept / [d]ecline cursor.
        self.assertIn("Install SDLC kit", out)
        self.assertIn("This adds the default Cypilot SDLC templates", out)
        self.assertIn("Reply with `a` to install it now or `d` to skip it", out)
        self.assertIn("Suggested: `a` for first-time setup", out)
        self.assertIn("`a` = download and install the default kit now", out)
        self.assertIn("[a]ccept / [d]ecline", out)

    def test_interactive_tty_decline(self):
        """User types 'd' → declined."""
        with patch("sys.stdin.isatty", return_value=True), \
             patch("sys.stderr", io.StringIO()), \
             patch("builtins.input", return_value="d"):
            self.assertFalse(self._fn()(True))

    def test_interactive_tty_accept_word(self):
        """User types 'accept' (full word) → accepted."""
        with patch("sys.stdin.isatty", return_value=True), \
             patch("sys.stderr", io.StringIO()), \
             patch("builtins.input", return_value="ACCEPT"):
            self.assertTrue(self._fn()(True))

    def test_interactive_tty_eof_declines(self):
        """EOF on input → treated as decline."""
        def _raise_eof():
            raise EOFError
        with patch("sys.stdin.isatty", return_value=True), \
             patch("sys.stderr", io.StringIO()), \
             patch("builtins.input", side_effect=_raise_eof):
            self.assertFalse(self._fn()(True))


if __name__ == "__main__":
    unittest.main()
