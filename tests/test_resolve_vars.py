"""
Tests for resolve-vars command.

Covers _collect_all_variables(), cmd_resolve_vars CLI, and info integration.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.commands.resolve_vars import _collect_all_variables, cmd_resolve_vars
from cypilot.utils.ui import set_json_mode


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bootstrap_project(root: Path, adapter_rel: str = "cypilot") -> Path:
    """Set up a minimal initialized project."""
    root.mkdir(parents=True, exist_ok=True)
    (root / ".git").mkdir(exist_ok=True)
    (root / "AGENTS.md").write_text(
        f'<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "{adapter_rel}"\n```\n<!-- /@cpt:root-agents -->\n',
        encoding="utf-8",
    )
    adapter = root / adapter_rel
    config = adapter / "config"
    for d in [adapter, config, adapter / ".core", adapter / ".gen"]:
        d.mkdir(parents=True, exist_ok=True)
    (config / "AGENTS.md").write_text("# Test\n", encoding="utf-8")
    return adapter


def _write_core_toml(config_dir: Path, data: dict) -> None:
    from cypilot.utils import toml_utils
    config_dir.mkdir(parents=True, exist_ok=True)
    toml_utils.dump(data, config_dir / "core.toml")


# ---------------------------------------------------------------------------
# _collect_all_variables (unit tests)
# ---------------------------------------------------------------------------

class TestCollectAllVariables(unittest.TestCase):
    """Unit tests for _collect_all_variables()."""

    def test_system_vars_always_present(self):
        """System variables (cypilot_path, project_root) always present."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            result = _collect_all_variables(root, adapter, None)
            self.assertIn("cypilot_path", result["variables"])
            self.assertIn("project_root", result["variables"])
            self.assertEqual(
                result["variables"]["cypilot_path"],
                adapter.resolve().as_posix(),
            )
            self.assertEqual(
                result["variables"]["project_root"],
                root.resolve().as_posix(),
            )

    def test_kit_resources_resolved(self):
        """Kit resource bindings are resolved to absolute paths."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            _write_core_toml(config, {
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {
                        "format": "Cypilot",
                        "path": "config/kits/sdlc",
                        "version": "2.0",
                        "resources": {
                            "adr_template": {"path": "config/kits/sdlc/artifacts/ADR/template.md"},
                            "scripts": {"path": "config/kits/sdlc/scripts"},
                        },
                    },
                },
            })

            result = _collect_all_variables(root, adapter, {
                "version": "1.0",
                "kits": {
                    "sdlc": {
                        "resources": {
                            "adr_template": {"path": "config/kits/sdlc/artifacts/ADR/template.md"},
                            "scripts": {"path": "config/kits/sdlc/scripts"},
                        },
                    },
                },
            })

            self.assertIn("adr_template", result["variables"])
            self.assertIn("scripts", result["variables"])
            self.assertTrue(result["variables"]["adr_template"].endswith(
                "config/kits/sdlc/artifacts/ADR/template.md"
            ))
            # Check structured output
            self.assertIn("sdlc", result["kits"])
            self.assertIn("adr_template", result["kits"]["sdlc"])

    def test_no_kits_returns_system_only(self):
        """Without kits, only system variables returned."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            result = _collect_all_variables(root, adapter, {
                "version": "1.0",
                "kits": {},
            })
            self.assertEqual(len(result["kits"]), 0)
            self.assertIn("cypilot_path", result["variables"])
            self.assertEqual(len(result["variables"]), 2)  # cypilot_path + project_root

    def test_kit_without_resources_skipped(self):
        """Kit without resources section produces no kit variables."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            result = _collect_all_variables(root, adapter, {
                "version": "1.0",
                "kits": {
                    "legacykit": {
                        "format": "Cypilot",
                        "path": "config/kits/legacykit",
                    },
                },
            })
            self.assertEqual(len(result["kits"]), 0)

    def test_multiple_kits_merged(self):
        """Resources from multiple kits merged into flat dict."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            result = _collect_all_variables(root, adapter, {
                "version": "1.0",
                "kits": {
                    "kit_a": {
                        "resources": {"var_a": {"path": "a/path"}},
                    },
                    "kit_b": {
                        "resources": {"var_b": {"path": "b/path"}},
                    },
                },
            })
            self.assertIn("var_a", result["variables"])
            self.assertIn("var_b", result["variables"])
            self.assertIn("kit_a", result["kits"])
            self.assertIn("kit_b", result["kits"])

    def test_string_binding_resolved(self):
        """Resource binding as plain string (not dict) is resolved."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            result = _collect_all_variables(root, adapter, {
                "kits": {
                    "mykit": {
                        "resources": {"readme": "docs/README.md"},
                    },
                },
            })
            self.assertIn("readme", result["variables"])
            self.assertTrue(result["variables"]["readme"].endswith("docs/README.md"))

    def test_empty_path_skipped(self):
        """Binding with empty path is silently skipped."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            result = _collect_all_variables(root, adapter, {
                "kits": {
                    "mykit": {
                        "resources": {
                            "good": {"path": "some/path"},
                            "bad": {"path": ""},
                        },
                    },
                },
            })
            self.assertIn("good", result["variables"])
            self.assertNotIn("bad", result["variables"])

    def test_non_dict_binding_skipped(self):
        """Non-dict non-string binding is silently skipped."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            result = _collect_all_variables(root, adapter, {
                "kits": {
                    "mykit": {
                        "resources": {
                            "good": {"path": "x"},
                            "bad": 42,
                        },
                    },
                },
            })
            self.assertIn("good", result["variables"])
            self.assertNotIn("bad", result["variables"])


# ---------------------------------------------------------------------------
# cmd_resolve_vars CLI (integration tests)
# ---------------------------------------------------------------------------

class TestCmdResolveVars(unittest.TestCase):
    """Integration tests for the resolve-vars CLI command."""

    def setUp(self):
        set_json_mode(True)

    def tearDown(self):
        set_json_mode(False)

    def test_basic_resolve(self):
        """resolve-vars returns system + kit variables."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            _write_core_toml(config, {
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {
                        "resources": {
                            "adr_template": {"path": "config/kits/sdlc/artifacts/ADR/template.md"},
                        },
                    },
                },
            })

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_resolve_vars(["--root", str(root)])
            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            self.assertEqual(out["status"], "OK")
            self.assertIn("cypilot_path", out["variables"])
            self.assertIn("adr_template", out["variables"])

    def test_filter_by_kit(self):
        """--kit filters to a single kit."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            _write_core_toml(config, {
                "version": "1.0",
                "kits": {
                    "sdlc": {
                        "resources": {"var_a": {"path": "a"}},
                    },
                    "other": {
                        "resources": {"var_b": {"path": "b"}},
                    },
                },
            })

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_resolve_vars(["--root", str(root), "--kit", "sdlc"])
            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            self.assertIn("var_a", out["variables"])
            self.assertNotIn("var_b", out["variables"])
            self.assertIn("sdlc", out["kits"])
            self.assertNotIn("other", out["kits"])

    def test_filter_by_nonexistent_kit(self):
        """--kit with unknown slug returns error."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            _write_core_toml(config, {
                "version": "1.0",
                "kits": {},
            })

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_resolve_vars(["--root", str(root), "--kit", "nope"])
            self.assertEqual(rc, 1)
            out = json.loads(buf.getvalue())
            self.assertEqual(out["status"], "ERROR")

    def test_flat_mode(self):
        """--flat outputs only the flat variables dict."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            _write_core_toml(config, {
                "version": "1.0",
                "kits": {
                    "sdlc": {
                        "resources": {"adr_rules": {"path": "config/kits/sdlc/artifacts/ADR/rules.md"}},
                    },
                },
            })

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_resolve_vars(["--root", str(root), "--flat"])
            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            # Flat mode wraps variables with metadata (no "status" key)
            self.assertNotIn("status", out)
            self.assertIn("variables", out)
            self.assertIn("cypilot_path", out["variables"])
            self.assertIn("adr_rules", out["variables"])

    def test_flat_with_kit_filter(self):
        """--flat combined with --kit returns only filtered flat dict."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            _write_core_toml(config, {
                "version": "1.0",
                "kits": {
                    "sdlc": {
                        "resources": {"var_a": {"path": "a"}},
                    },
                    "other": {
                        "resources": {"var_b": {"path": "b"}},
                    },
                },
            })

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_resolve_vars(["--root", str(root), "--kit", "sdlc", "--flat"])
            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            # Flat mode wraps variables with metadata (no "status" key)
            self.assertNotIn("status", out)
            self.assertIn("variables", out)
            # System vars present
            self.assertIn("cypilot_path", out["variables"])
            # Only sdlc kit var, not other
            self.assertIn("var_a", out["variables"])
            self.assertNotIn("var_b", out["variables"])

    def test_no_project_root(self):
        """Returns error when no project root found."""
        with TemporaryDirectory() as td:
            empty = Path(td) / "empty"
            empty.mkdir()

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_resolve_vars(["--root", str(empty)])
            self.assertEqual(rc, 1)
            out = json.loads(buf.getvalue())
            self.assertEqual(out["status"], "ERROR")

    def test_no_cypilot_dir(self):
        """Returns error when cypilot not initialized."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            root.mkdir()
            (root / ".git").mkdir()

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_resolve_vars(["--root", str(root)])
            self.assertEqual(rc, 1)
            out = json.loads(buf.getvalue())
            self.assertEqual(out["status"], "ERROR")


# ---------------------------------------------------------------------------
# info integration — variables in info output
# ---------------------------------------------------------------------------

class TestInfoVariablesIntegration(unittest.TestCase):
    """Test that cpt info includes variables from resolve-vars."""

    def setUp(self):
        set_json_mode(True)

    def tearDown(self):
        set_json_mode(False)

    def test_info_includes_variables(self):
        """cpt info output contains variables dict."""
        from cypilot.commands.adapter_info import cmd_adapter_info

        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            _write_core_toml(config, {
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {
                        "format": "Cypilot",
                        "path": "config/kits/sdlc",
                        "version": "2.0",
                        "resources": {
                            "adr_template": {"path": "config/kits/sdlc/artifacts/ADR/template.md"},
                            "scripts": {"path": "config/kits/sdlc/scripts"},
                        },
                    },
                },
            })

            kit_dir = config / "kits" / "sdlc"
            kit_dir.mkdir(parents=True)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_adapter_info(["--root", str(root)])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                variables = out.get("variables", {})
                self.assertIn("cypilot_path", variables)
                self.assertIn("project_root", variables)
                self.assertIn("adr_template", variables)
                self.assertIn("scripts", variables)
            finally:
                os.chdir(cwd)

    def test_info_includes_variables_by_kit(self):
        """cpt info output contains variables_by_kit dict."""
        from cypilot.commands.adapter_info import cmd_adapter_info

        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            _write_core_toml(config, {
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {
                        "format": "Cypilot",
                        "path": "config/kits/sdlc",
                        "version": "2.0",
                        "resources": {
                            "adr_template": {"path": "config/kits/sdlc/artifacts/ADR/template.md"},
                        },
                    },
                },
            })

            kit_dir = config / "kits" / "sdlc"
            kit_dir.mkdir(parents=True)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_adapter_info(["--root", str(root)])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                by_kit = out.get("variables_by_kit", {})
                self.assertIn("sdlc", by_kit)
                self.assertIn("adr_template", by_kit["sdlc"])
            finally:
                os.chdir(cwd)

    def test_info_includes_collision_flag(self):
        """cpt info output contains variables_collisions when collision exists."""
        from cypilot.commands.adapter_info import cmd_adapter_info

        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            _write_core_toml(config, {
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "kit_a": {
                        "resources": {"dup_var": {"path": "a/file"}},
                    },
                    "kit_b": {
                        "resources": {"dup_var": {"path": "b/file"}},
                    },
                },
            })

            kit_dir_a = config / "kits" / "kit_a"
            kit_dir_a.mkdir(parents=True)
            kit_dir_b = config / "kits" / "kit_b"
            kit_dir_b.mkdir(parents=True)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_adapter_info(["--root", str(root)])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertIn("variables_collisions", out)
                self.assertEqual(len(out["variables_collisions"]), 1)
                self.assertEqual(out["variables_collisions"][0]["variable"], "dup_var")
            finally:
                os.chdir(cwd)

    def test_info_degraded_on_corrupt_core_toml(self):
        """cpt info sets variables_degraded when core.toml is corrupt."""
        from cypilot.commands.adapter_info import cmd_adapter_info

        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            config.mkdir(parents=True, exist_ok=True)
            (config / "core.toml").write_text("{{INVALID TOML", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(root)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_adapter_info(["--root", str(root)])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                self.assertTrue(out.get("variables_degraded"))
                self.assertIn("core.toml load failed", out.get("variables_error", ""))
                self.assertIsNone(out.get("variables"))
            finally:
                os.chdir(cwd)

    def test_info_variables_empty_when_no_kits(self):
        """cpt info variables has only system vars when no kit resources."""
        from cypilot.commands.adapter_info import cmd_adapter_info

        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            _write_core_toml(config, {
                "version": "1.0",
                "project_root": "..",
                "kits": {},
            })

            cwd = os.getcwd()
            try:
                os.chdir(root)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_adapter_info(["--root", str(root)])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                variables = out.get("variables", {})
                self.assertIn("cypilot_path", variables)
                self.assertIn("project_root", variables)
                # System vars only (cypilot_path + project_root)
                self.assertEqual(len(variables), 2)
            finally:
                os.chdir(cwd)


# ---------------------------------------------------------------------------
# CLI dispatch via main()
# ---------------------------------------------------------------------------

class TestResolveVarsCLIDispatch(unittest.TestCase):
    """Test that resolve-vars is wired into the CLI main dispatcher."""

    def setUp(self):
        set_json_mode(True)

    def tearDown(self):
        set_json_mode(False)

    def test_cli_dispatch(self):
        """main(['resolve-vars', ...]) dispatches correctly."""
        from cypilot.cli import main

        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            _write_core_toml(config, {
                "version": "1.0",
                "kits": {},
            })

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["resolve-vars", "--root", str(root)])
            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            self.assertEqual(out["status"], "OK")
            self.assertIn("variables", out)

    def test_cli_help_includes_resolve_vars(self):
        """CLI help output lists resolve-vars command."""
        from cypilot.cli import main

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["--help"])
        self.assertEqual(rc, 0)
        out = json.loads(buf.getvalue())
        self.assertIn("resolve-vars", out.get("commands", {}))


# ---------------------------------------------------------------------------
# Edge cases for coverage
# ---------------------------------------------------------------------------

class TestCollectAllVariablesEdgeCases(unittest.TestCase):
    """Cover edge branches in _collect_all_variables."""

    def test_non_dict_kit_entry_skipped(self):
        """Kit entry that is not a dict (e.g. a string) is skipped."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            result = _collect_all_variables(root, adapter, {
                "kits": {
                    "bad_kit": "not-a-dict",
                    "good_kit": {
                        "resources": {"var_x": {"path": "x/y"}},
                    },
                },
            })
            self.assertNotIn("bad_kit", result["kits"])
            self.assertIn("good_kit", result["kits"])
            self.assertIn("var_x", result["variables"])

    def test_collision_detected_different_paths(self):
        """Duplicate var_name across kits with different paths records collision."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            result = _collect_all_variables(root, adapter, {
                "kits": {
                    "kit_a": {
                        "resources": {"shared_var": {"path": "a/path"}},
                    },
                    "kit_b": {
                        "resources": {"shared_var": {"path": "b/path"}},
                    },
                },
            })
            # First-writer-wins: kit_a's value kept
            self.assertTrue(result["variables"]["shared_var"].endswith("a/path"))
            # Collision recorded
            self.assertIn("collisions", result)
            self.assertEqual(len(result["collisions"]), 1)
            c = result["collisions"][0]
            self.assertEqual(c["variable"], "shared_var")
            self.assertEqual(c["kit"], "kit_b")
            self.assertTrue(c["path"].endswith("b/path") or c["path"] == (adapter / "b/path").resolve().as_posix())

    def test_no_collision_same_path(self):
        """Same var_name with identical path across kits is NOT a collision."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            result = _collect_all_variables(root, adapter, {
                "kits": {
                    "kit_a": {
                        "resources": {"shared_var": {"path": "same/path"}},
                    },
                    "kit_b": {
                        "resources": {"shared_var": {"path": "same/path"}},
                    },
                },
            })
            self.assertNotIn("collisions", result)
            self.assertIn("shared_var", result["variables"])

    def test_non_string_path_in_dict_binding_skipped(self):
        """Dict binding with non-string path (e.g. int) is skipped."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            result = _collect_all_variables(root, adapter, {
                "kits": {
                    "mykit": {
                        "resources": {
                            "good": {"path": "valid/path"},
                            "int_path": {"path": 42},
                            "list_path": {"path": ["a", "b"]},
                            "none_path": {"path": None},
                        },
                    },
                },
            })
            self.assertIn("good", result["variables"])
            self.assertNotIn("int_path", result["variables"])
            self.assertNotIn("list_path", result["variables"])
            self.assertNotIn("none_path", result["variables"])


class TestCmdResolveVarsCorruptToml(unittest.TestCase):
    """Cover corrupt core.toml branch."""

    def setUp(self):
        set_json_mode(True)

    def tearDown(self):
        set_json_mode(False)

    def test_corrupt_core_toml(self):
        """Corrupt core.toml is handled gracefully (variables still resolve system vars)."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            config.mkdir(parents=True, exist_ok=True)
            (config / "core.toml").write_text("{{INVALID TOML", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_resolve_vars(["--root", str(root)])
            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            self.assertIn("cypilot_path", out["variables"])
            # No kit vars since core.toml is corrupt
            self.assertEqual(len(out["kits"]), 0)
            # Parse error propagated as core_load_error
            self.assertIn("core_load_error", out)
            self.assertIn("TOMLDecodeError", out["core_load_error"])


# ---------------------------------------------------------------------------
# Human formatter coverage (non-JSON mode)
# ---------------------------------------------------------------------------

class TestHumanFormatters(unittest.TestCase):
    """Cover _human_flat and _human_structured formatters."""

    def test_human_flat_output(self):
        """_human_flat produces output without error."""
        from cypilot.commands.resolve_vars import _human_flat
        set_json_mode(False)
        try:
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                _human_flat({"variables": {
                    "cypilot_path": "/tmp/test/cypilot",
                    "adr_template": "/tmp/test/cypilot/config/kits/sdlc/artifacts/ADR/template.md",
                }})
            output = buf.getvalue()
            self.assertIn("cypilot_path", output)
            self.assertIn("adr_template", output)
        finally:
            set_json_mode(True)

    def test_human_structured_output(self):
        """_human_structured produces output with system, kits, and summary."""
        from cypilot.commands.resolve_vars import _human_structured
        set_json_mode(False)
        try:
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                _human_structured({
                    "status": "OK",
                    "system": {
                        "cypilot_path": "/tmp/test/cypilot",
                        "project_root": "/tmp/test",
                    },
                    "kits": {
                        "sdlc": {
                            "adr_template": "/tmp/test/cypilot/config/kits/sdlc/artifacts/ADR/template.md",
                        },
                    },
                    "variables": {
                        "cypilot_path": "/tmp/test/cypilot",
                        "project_root": "/tmp/test",
                        "adr_template": "/tmp/test/cypilot/config/kits/sdlc/artifacts/ADR/template.md",
                    },
                })
            output = buf.getvalue()
            self.assertIn("System", output)
            self.assertIn("sdlc", output)
            self.assertIn("Total: 3", output)
        finally:
            set_json_mode(True)

    def test_human_structured_empty_kits(self):
        """_human_structured with no kits still shows system and summary."""
        from cypilot.commands.resolve_vars import _human_structured
        set_json_mode(False)
        try:
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                _human_structured({
                    "status": "OK",
                    "system": {"cypilot_path": "/tmp/x"},
                    "kits": {},
                    "variables": {"cypilot_path": "/tmp/x"},
                })
            output = buf.getvalue()
            self.assertIn("System", output)
            self.assertIn("Total: 1", output)
        finally:
            set_json_mode(True)

    def test_cmd_human_mode_structured(self):
        """cmd_resolve_vars in non-JSON mode calls _human_structured."""
        set_json_mode(False)
        try:
            with TemporaryDirectory() as td:
                root = Path(td) / "proj"
                adapter = _bootstrap_project(root)
                config = adapter / "config"
                _write_core_toml(config, {
                    "version": "1.0",
                    "kits": {"sdlc": {"resources": {"var_a": {"path": "a"}}}},
                })
                buf = io.StringIO()
                with contextlib.redirect_stderr(buf):
                    rc = cmd_resolve_vars(["--root", str(root)])
                self.assertEqual(rc, 0)
                output = buf.getvalue()
                self.assertIn("System", output)
                self.assertIn("var_a", output)
        finally:
            set_json_mode(True)

    def test_cmd_human_mode_flat(self):
        """cmd_resolve_vars --flat in non-JSON mode calls _human_flat."""
        set_json_mode(False)
        try:
            with TemporaryDirectory() as td:
                root = Path(td) / "proj"
                adapter = _bootstrap_project(root)
                config = adapter / "config"
                _write_core_toml(config, {
                    "version": "1.0",
                    "kits": {},
                })
                buf = io.StringIO()
                with contextlib.redirect_stderr(buf):
                    rc = cmd_resolve_vars(["--root", str(root), "--flat"])
                self.assertEqual(rc, 0)
                output = buf.getvalue()
                self.assertIn("cypilot_path", output)
        finally:
            set_json_mode(True)


# ---------------------------------------------------------------------------
# Layer variables wiring (base_dir, master_repo, repo)
# ---------------------------------------------------------------------------

class TestResolveVarsLayerVariables(unittest.TestCase):
    """Test that resolve-vars CLI exposes layer variables (base_dir, master_repo, repo)."""

    def setUp(self):
        set_json_mode(True)

    def tearDown(self):
        set_json_mode(False)

    def test_resolve_vars_includes_layer_variables(self):
        """resolve-vars output contains base_dir, master_repo, and repo."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            _write_core_toml(config, {
                "version": "1.0",
                "kits": {},
            })

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_resolve_vars(["--root", str(root)])
            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            variables = out["variables"]
            self.assertIn("base_dir", variables)
            self.assertIn("master_repo", variables)
            self.assertIn("repo", variables)
            # repo should be the resolved project root
            self.assertEqual(variables["repo"], root.resolve().as_posix())

    def test_resolve_vars_flat_includes_layer_variables(self):
        """resolve-vars --flat output contains base_dir, master_repo, and repo."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            _write_core_toml(config, {
                "version": "1.0",
                "kits": {},
            })

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_resolve_vars(["--root", str(root), "--flat"])
            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            variables = out["variables"]
            self.assertIn("base_dir", variables)
            self.assertIn("master_repo", variables)
            self.assertIn("repo", variables)


class TestResolveVarsKitLayerVariables(unittest.TestCase):
    """Test that --kit and --kit --flat preserve layer variables."""

    def setUp(self):
        set_json_mode(True)

    def tearDown(self):
        set_json_mode(False)

    def test_kit_includes_layer_variables(self):
        """resolve-vars --kit includes base_dir, master_repo, and repo."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            _write_core_toml(config, {
                "version": "1.0",
                "kits": {
                    "sdlc": {
                        "resources": {"var_a": {"path": "a"}},
                    },
                },
            })

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_resolve_vars(["--root", str(root), "--kit", "sdlc"])
            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            variables = out["variables"]
            self.assertIn("base_dir", variables)
            self.assertIn("master_repo", variables)
            self.assertIn("repo", variables)
            self.assertEqual(variables["repo"], root.resolve().as_posix())
            # Kit var still present
            self.assertIn("var_a", variables)

    def test_kit_flat_includes_layer_variables(self):
        """resolve-vars --kit --flat includes base_dir, master_repo, and repo."""
        with TemporaryDirectory() as td:
            root = Path(td) / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            _write_core_toml(config, {
                "version": "1.0",
                "kits": {
                    "sdlc": {
                        "resources": {"var_a": {"path": "a"}},
                    },
                    "other": {
                        "resources": {"var_b": {"path": "b"}},
                    },
                },
            })

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_resolve_vars(["--root", str(root), "--kit", "sdlc", "--flat"])
            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            variables = out["variables"]
            self.assertIn("base_dir", variables)
            self.assertIn("master_repo", variables)
            self.assertIn("repo", variables)
            # Only selected kit var, not other
            self.assertIn("var_a", variables)
            self.assertNotIn("var_b", variables)


if __name__ == "__main__":
    unittest.main()
