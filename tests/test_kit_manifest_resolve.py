"""Tests for WP5: Resource Resolution API + cpt info.

Covers resolve_resource_bindings(), LoadedKit.resource_bindings,
and cpt info resource output for manifest-driven kits.
"""
from __future__ import annotations

import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))

from cypilot.utils.manifest import resolve_resource_bindings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_core_toml(config_dir: Path, data: dict) -> Path:
    """Write core.toml into *config_dir* and return the path."""
    from cypilot.utils import toml_utils
    config_dir.mkdir(parents=True, exist_ok=True)
    core_path = config_dir / "core.toml"
    toml_utils.dump(data, core_path)
    return core_path


def _bootstrap_project(root: Path, adapter_rel: str = "cypilot") -> Path:
    """Set up a minimal initialized project for kit commands."""
    root.mkdir(parents=True, exist_ok=True)
    (root / ".git").mkdir(exist_ok=True)
    (root / "AGENTS.md").write_text(
        f'<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "{adapter_rel}"\n```\n<!-- /@cpt:root-agents -->\n',
        encoding="utf-8",
    )
    adapter = root / adapter_rel
    config = adapter / "config"
    gen = adapter / ".gen"
    for d in [adapter, config, gen, adapter / ".core"]:
        d.mkdir(parents=True, exist_ok=True)
    (config / "AGENTS.md").write_text("# Test\n", encoding="utf-8")
    from cypilot.utils import toml_utils
    toml_utils.dump({
        "version": "1.0",
        "project_root": "..",
        "kits": {},
    }, config / "core.toml")
    toml_utils.dump({
        "systems": [{"name": "TestProject", "slug": "test"}],
    }, config / "artifacts.toml")
    return adapter


# ---------------------------------------------------------------------------
# resolve_resource_bindings (unit tests)
# ---------------------------------------------------------------------------

class TestResolveResourceBindings(unittest.TestCase):
    """Unit tests for resolve_resource_bindings()."""

    def test_returns_correct_absolute_paths(self):
        """Resource bindings are resolved to absolute paths against cypilot_dir."""
        with TemporaryDirectory() as td:
            td_path = Path(td)
            cypilot_dir = td_path / "proj" / "cypilot"
            cypilot_dir.mkdir(parents=True)
            config_dir = td_path / "config"

            _write_core_toml(config_dir, {
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "mykit": {
                        "format": "Cypilot",
                        "path": "config/kits/mykit",
                        "version": "2.0",
                        "resources": {
                            "adr_artifacts": {"path": "config/kits/mykit/artifacts/ADR"},
                            "constraints": {"path": "config/kits/mykit/constraints.toml"},
                        },
                    },
                },
            })

            result = resolve_resource_bindings(config_dir, "mykit", cypilot_dir)

            self.assertEqual(len(result), 2)
            self.assertIn("adr_artifacts", result)
            self.assertIn("constraints", result)
            self.assertIsInstance(result["adr_artifacts"], Path)
            self.assertTrue(result["adr_artifacts"].is_absolute())
            self.assertEqual(
                result["adr_artifacts"],
                (cypilot_dir / "config/kits/mykit/artifacts/ADR").resolve(),
            )
            self.assertEqual(
                result["constraints"],
                (cypilot_dir / "config/kits/mykit/constraints.toml").resolve(),
            )

    def test_same_os_absolute_binding_preserved(self):
        """Same-OS absolute resource bindings stay absolute."""
        with TemporaryDirectory() as td:
            td_path = Path(td)
            cypilot_dir = td_path / "proj" / "cypilot"
            cypilot_dir.mkdir(parents=True)
            config_dir = td_path / "config"
            absolute_target = (td_path / "external" / "constraints.toml").resolve()

            _write_core_toml(config_dir, {
                "version": "1.0",
                "kits": {
                    "mykit": {
                        "resources": {
                            "constraints": {"path": str(absolute_target)},
                        },
                    },
                },
            })

            result = resolve_resource_bindings(config_dir, "mykit", cypilot_dir)

            self.assertEqual(result["constraints"], absolute_target)

    def test_preserves_absolute_binding_after_relpath_fallback_behavior(self):
        """Absolute bindings serialized via relpath fallback stay absolute when resolved."""
        import cypilot.commands.kit as kit_module
        from cypilot.commands.kit import _serialize_manifest_binding_path

        with TemporaryDirectory() as td:
            td_path = Path(td)
            cypilot_dir = td_path / "proj" / "cypilot"
            cypilot_dir.mkdir(parents=True)
            config_dir = td_path / "config"
            absolute_target = (td_path / "external" / "SKILL.md").resolve()

            with patch.object(
                kit_module.os.path,
                "relpath",
                side_effect=ValueError("cross-device fallback"),
            ):
                binding_path = _serialize_manifest_binding_path(absolute_target, cypilot_dir)

            _write_core_toml(config_dir, {
                "version": "1.0",
                "kits": {
                    "mykit": {
                        "resources": {
                            "skill": {"path": binding_path},
                        },
                    },
                },
            })

            result = resolve_resource_bindings(config_dir, "mykit", cypilot_dir)

            self.assertEqual(result["skill"], absolute_target)

    def test_windows_absolute_binding_on_non_windows_fails_explicitly(self):
        """Windows absolute bindings are rejected on non-Windows hosts."""
        if os.name == "nt":
            self.skipTest("Windows absolute cross-OS regression applies to non-Windows hosts")
        with TemporaryDirectory() as td:
            td_path = Path(td)
            cypilot_dir = td_path / "cypilot"
            cypilot_dir.mkdir()
            config_dir = td_path / "config"

            _write_core_toml(config_dir, {
                "version": "1.0",
                "kits": {
                    "mykit": {
                        "resources": {
                            "constraints": {"path": "C:/external-kits/sdlc/constraints.toml"},
                        },
                    },
                },
            })

            with self.assertRaisesRegex(ValueError, "not accessible on this OS"):
                resolve_resource_bindings(config_dir, "mykit", cypilot_dir)

    def test_posix_absolute_binding_on_windows_fails_explicitly(self):
        """POSIX absolute bindings are rejected on Windows hosts."""
        if os.name != "nt":
            self.skipTest("POSIX absolute cross-OS regression applies to Windows hosts")
        with TemporaryDirectory() as td:
            td_path = Path(td)
            cypilot_dir = td_path / "cypilot"
            cypilot_dir.mkdir()
            config_dir = td_path / "config"

            _write_core_toml(config_dir, {
                "version": "1.0",
                "kits": {
                    "mykit": {
                        "resources": {
                            "constraints": {"path": "/opt/cypilot/constraints.toml"},
                        },
                    },
                },
            })

            with self.assertRaisesRegex(ValueError, "not accessible on this OS"):
                resolve_resource_bindings(config_dir, "mykit", cypilot_dir)

    def test_missing_resources_section_returns_empty(self):
        """Kit without resources section → empty dict."""
        with TemporaryDirectory() as td:
            td_path = Path(td)
            cypilot_dir = td_path / "proj" / "cypilot"
            cypilot_dir.mkdir(parents=True)
            config_dir = td_path / "config"

            _write_core_toml(config_dir, {
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "legacykit": {
                        "format": "Cypilot",
                        "path": "config/kits/legacykit",
                        "version": "1.0",
                    },
                },
            })

            result = resolve_resource_bindings(config_dir, "legacykit", cypilot_dir)
            self.assertEqual(result, {})

    def test_missing_kit_returns_empty(self):
        """Non-existent kit slug → empty dict."""
        with TemporaryDirectory() as td:
            td_path = Path(td)
            cypilot_dir = td_path / "proj" / "cypilot"
            cypilot_dir.mkdir(parents=True)
            config_dir = td_path / "config"

            _write_core_toml(config_dir, {
                "version": "1.0",
                "project_root": "..",
                "kits": {},
            })

            result = resolve_resource_bindings(config_dir, "nokit", cypilot_dir)
            self.assertEqual(result, {})

    def test_missing_core_toml_returns_empty(self):
        """No core.toml file → empty dict."""
        with TemporaryDirectory() as td:
            td_path = Path(td)
            config_dir = td_path / "config"
            config_dir.mkdir()
            cypilot_dir = td_path / "cypilot"
            cypilot_dir.mkdir()

            result = resolve_resource_bindings(config_dir, "mykit", cypilot_dir)
            self.assertEqual(result, {})

    def test_empty_path_binding_skipped(self):
        """Binding with empty path is skipped."""
        with TemporaryDirectory() as td:
            td_path = Path(td)
            cypilot_dir = td_path / "cypilot"
            cypilot_dir.mkdir()
            config_dir = td_path / "config"

            _write_core_toml(config_dir, {
                "version": "1.0",
                "kits": {
                    "mykit": {
                        "resources": {
                            "good": {"path": "some/path"},
                            "bad": {"path": ""},
                        },
                    },
                },
            })

            result = resolve_resource_bindings(config_dir, "mykit", cypilot_dir)
            self.assertEqual(len(result), 1)
            self.assertIn("good", result)
            self.assertNotIn("bad", result)

    def test_corrupted_core_toml_returns_empty(self):
        """Corrupted core.toml that can't be parsed → empty dict."""
        with TemporaryDirectory() as td:
            td_path = Path(td)
            cypilot_dir = td_path / "cypilot"
            cypilot_dir.mkdir()
            config_dir = td_path / "config"
            config_dir.mkdir(parents=True)
            (config_dir / "core.toml").write_text("[broken\ninvalid", encoding="utf-8")

            result = resolve_resource_bindings(config_dir, "mykit", cypilot_dir)
            self.assertEqual(result, {})

    def test_kits_not_a_dict_returns_empty(self):
        """core.toml with kits = 'string' instead of table → empty dict."""
        with TemporaryDirectory() as td:
            td_path = Path(td)
            cypilot_dir = td_path / "cypilot"
            cypilot_dir.mkdir()
            config_dir = td_path / "config"
            config_dir.mkdir(parents=True)
            (config_dir / "core.toml").write_text(
                'version = "1.0"\nkits = "not_a_dict"\n', encoding="utf-8",
            )

            result = resolve_resource_bindings(config_dir, "mykit", cypilot_dir)
            self.assertEqual(result, {})

    def test_string_binding_resolved(self):
        """Resource binding as plain string (not dict) is resolved."""
        with TemporaryDirectory() as td:
            td_path = Path(td)
            cypilot_dir = td_path / "cypilot"
            cypilot_dir.mkdir()
            config_dir = td_path / "config"

            _write_core_toml(config_dir, {
                "version": "1.0",
                "kits": {
                    "mykit": {
                        "resources": {
                            "readme": "docs/README.md",
                        },
                    },
                },
            })

            result = resolve_resource_bindings(config_dir, "mykit", cypilot_dir)
            self.assertEqual(len(result), 1)
            self.assertIn("readme", result)
            self.assertEqual(
                result["readme"],
                (cypilot_dir / "docs/README.md").resolve(),
            )

    def test_non_dict_non_string_binding_skipped(self):
        """Resource binding as an integer is silently skipped."""
        with TemporaryDirectory() as td:
            td_path = Path(td)
            cypilot_dir = td_path / "cypilot"
            cypilot_dir.mkdir()
            config_dir = td_path / "config"

            _write_core_toml(config_dir, {
                "version": "1.0",
                "kits": {
                    "mykit": {
                        "resources": {
                            "good": {"path": "some/path"},
                            "bad": 42,
                        },
                    },
                },
            })

            result = resolve_resource_bindings(config_dir, "mykit", cypilot_dir)
            self.assertEqual(len(result), 1)
            self.assertIn("good", result)
            self.assertNotIn("bad", result)


# ---------------------------------------------------------------------------
# LoadedKit.resource_bindings (unit tests)
# ---------------------------------------------------------------------------

class TestLoadedKitResourceBindings(unittest.TestCase):
    """Test that LoadedKit includes resource_bindings from context loading."""

    def test_loaded_kit_has_resource_bindings_field(self):
        """LoadedKit dataclass accepts resource_bindings."""
        from cypilot.utils.context import LoadedKit
        from cypilot.utils.artifacts_meta import Kit

        kit = Kit(kit_id="mykit", format="Cypilot", path="config/kits/mykit")
        lk = LoadedKit(
            kit=kit,
            templates={},
            constraints=None,
            resource_bindings={"adr": "/abs/path/adr"},
        )
        self.assertEqual(lk.resource_bindings, {"adr": "/abs/path/adr"})

    def test_loaded_kit_default_none(self):
        """LoadedKit resource_bindings defaults to None."""
        from cypilot.utils.context import LoadedKit
        from cypilot.utils.artifacts_meta import Kit

        kit = Kit(kit_id="mykit", format="Cypilot", path="config/kits/mykit")
        lk = LoadedKit(kit=kit, templates={})
        self.assertIsNone(lk.resource_bindings)

    def test_context_load_populates_resource_bindings(self):
        """CypilotContext.load() populates resource_bindings for manifest-driven kit."""
        from cypilot.utils.context import CypilotContext

        with TemporaryDirectory() as td:
            td_path = Path(td)
            root = td_path / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"

            # Install a kit with resources in core.toml
            from cypilot.utils import toml_utils
            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {
                        "format": "Cypilot",
                        "path": "config/kits/sdlc",
                        "version": "2.0",
                        "resources": {
                            "adr_artifacts": {"path": "config/kits/sdlc/artifacts/ADR"},
                        },
                    },
                },
            }, config / "core.toml")

            # Create artifacts.toml with the kit reference
            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {"format": "Cypilot", "path": "config/kits/sdlc"},
                },
                "systems": [{"name": "Test", "slug": "test", "kit": "sdlc"}],
            }, config / "artifacts.toml")

            # Create minimal kit dir for constraints loading
            kit_dir = config / "kits" / "sdlc"
            kit_dir.mkdir(parents=True)
            (kit_dir / "constraints.toml").write_text("[artifacts]\n", encoding="utf-8")

            ctx = CypilotContext.load(root)
            self.assertIsNotNone(ctx)
            self.assertIn("sdlc", ctx.kits)
            lk = ctx.kits["sdlc"]
            self.assertIsNotNone(lk.resource_bindings)
            self.assertIn("adr_artifacts", lk.resource_bindings)

    def test_context_load_preserves_same_os_absolute_kit_path(self):
        """CypilotContext.load() keeps same-OS absolute kits.{slug}.path absolute."""
        from cypilot.utils.context import CypilotContext

        with TemporaryDirectory() as td:
            td_path = Path(td)
            root = td_path / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            absolute_kit_dir = (td_path / "external" / "sdlc").resolve()
            absolute_kit_dir.mkdir(parents=True, exist_ok=True)
            (absolute_kit_dir / "constraints.toml").write_text("[artifacts]\n", encoding="utf-8")
            stale_registry_path = "config/kits/sdlc"

            from cypilot.utils import toml_utils
            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {
                        "format": "Cypilot",
                        "path": str(absolute_kit_dir),
                        "version": "2.0",
                    },
                },
            }, config / "core.toml")

            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {"format": "Cypilot", "path": stale_registry_path},
                },
                "systems": [{"name": "Test", "slug": "test", "kit": "sdlc"}],
            }, config / "artifacts.toml")

            ctx = CypilotContext.load(root)

            self.assertIsNotNone(ctx)
            self.assertIn("sdlc", ctx.kits)
            self.assertEqual(ctx.kits["sdlc"].kit.path, str(absolute_kit_dir))
            self.assertNotEqual(ctx.kits["sdlc"].kit.path, stale_registry_path)
            self.assertIsNotNone(ctx.kits["sdlc"].constraints)

    def test_context_load_preserves_same_os_absolute_binding(self):
        """CypilotContext.load() keeps same-OS absolute resource bindings absolute."""
        from cypilot.utils.context import CypilotContext

        with TemporaryDirectory() as td:
            td_path = Path(td)
            root = td_path / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            absolute_constraints = (td_path / "external" / "constraints.toml").resolve()
            absolute_constraints.parent.mkdir(parents=True, exist_ok=True)
            absolute_constraints.write_text("[artifacts]\n", encoding="utf-8")

            from cypilot.utils import toml_utils
            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {
                        "format": "Cypilot",
                        "path": "config/kits/sdlc",
                        "version": "2.0",
                        "resources": {
                            "constraints": {"path": str(absolute_constraints)},
                        },
                    },
                },
            }, config / "core.toml")

            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {"format": "Cypilot", "path": "config/kits/sdlc"},
                },
                "systems": [{"name": "Test", "slug": "test", "kit": "sdlc"}],
            }, config / "artifacts.toml")

            kit_dir = config / "kits" / "sdlc"
            kit_dir.mkdir(parents=True)

            ctx = CypilotContext.load(root)

            self.assertIsNotNone(ctx)
            self.assertEqual(
                ctx.kits["sdlc"].resource_bindings,
                {"constraints": str(absolute_constraints)},
            )

    def test_context_load_no_resources_is_none(self):
        """CypilotContext.load() leaves resource_bindings as None for legacy kit."""
        from cypilot.utils.context import CypilotContext

        with TemporaryDirectory() as td:
            td_path = Path(td)
            root = td_path / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"

            from cypilot.utils import toml_utils
            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {
                        "format": "Cypilot",
                        "path": "config/kits/sdlc",
                        "version": "1.0",
                    },
                },
            }, config / "core.toml")

            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {"format": "Cypilot", "path": "config/kits/sdlc"},
                },
                "systems": [{"name": "Test", "slug": "test", "kit": "sdlc"}],
            }, config / "artifacts.toml")

            kit_dir = config / "kits" / "sdlc"
            kit_dir.mkdir(parents=True)
            (kit_dir / "constraints.toml").write_text("[artifacts]\n", encoding="utf-8")

            ctx = CypilotContext.load(root)
            self.assertIsNotNone(ctx)
            self.assertIn("sdlc", ctx.kits)
            self.assertIsNone(ctx.kits["sdlc"].resource_bindings)


# ---------------------------------------------------------------------------
# cpt info resources output
# ---------------------------------------------------------------------------

class TestAdapterInfoResources(unittest.TestCase):
    """Test that cpt info includes resources per kit."""

    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(True)

    def tearDown(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

    def test_info_includes_resources_for_manifest_kit(self):
        """cpt info output contains resources for manifest-driven kit."""
        from cypilot.commands.adapter_info import cmd_adapter_info

        with TemporaryDirectory() as td:
            td_path = Path(td)
            root = td_path / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"

            from cypilot.utils import toml_utils
            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {
                        "format": "Cypilot",
                        "path": "config/kits/sdlc",
                        "version": "2.0",
                        "resources": {
                            "adr_artifacts": {"path": "config/kits/sdlc/artifacts/ADR"},
                            "constraints": {"path": "config/kits/sdlc/constraints.toml"},
                        },
                    },
                },
            }, config / "core.toml")

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
                kd = out.get("kit_details", {}).get("sdlc", {})
                self.assertIn("resources", kd)
                self.assertIn("adr_artifacts", kd["resources"])
                self.assertEqual(
                    kd["resources"]["adr_artifacts"]["path"],
                    "config/kits/sdlc/artifacts/ADR",
                )
            finally:
                os.chdir(cwd)

    def test_info_no_resources_for_legacy_kit(self):
        """cpt info output omits resources for legacy kit without resources."""
        from cypilot.commands.adapter_info import cmd_adapter_info

        with TemporaryDirectory() as td:
            td_path = Path(td)
            root = td_path / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"

            from cypilot.utils import toml_utils
            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "legacykit": {
                        "format": "Cypilot",
                        "path": "config/kits/legacykit",
                        "version": "1.0",
                    },
                },
            }, config / "core.toml")

            kit_dir = config / "kits" / "legacykit"
            kit_dir.mkdir(parents=True)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = cmd_adapter_info(["--root", str(root)])
                self.assertEqual(rc, 0)
                out = json.loads(buf.getvalue())
                kd = out.get("kit_details", {}).get("legacykit", {})
                self.assertNotIn("resources", kd)
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
