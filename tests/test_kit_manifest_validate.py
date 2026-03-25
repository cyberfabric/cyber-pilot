"""Tests for WP6: Validator Resource Path Resolution.

Covers:
- context.py: constraints loading via resource bindings
- validate_kits.py: resource path verification for manifest-driven kits
- validate_kits.py: standalone kit manifest validation
"""
from __future__ import annotations

import sys
import io
import json
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "cypilot" / "scripts"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def _write_core_toml(config_dir: Path, data: dict) -> Path:
    """Write core.toml into *config_dir* and return the path."""
    from cypilot.utils import toml_utils
    config_dir.mkdir(parents=True, exist_ok=True)
    core_path = config_dir / "core.toml"
    toml_utils.dump(data, core_path)
    return core_path


def _write_minimal_constraints(target_dir: Path) -> None:
    """Write a minimal valid constraints.toml into *target_dir*."""
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "constraints.toml").write_text("[artifacts]\n", encoding="utf-8")


def _write_manifest_toml(kit_dir: Path, resources: list[dict]) -> None:
    """Write a valid manifest.toml into *kit_dir*."""
    from cypilot.utils.toml_utils import dumps
    data = {
        "manifest": {
            "version": "1.0",
            "root": "{cypilot_path}/config/kits/{slug}",
            "user_modifiable": False,
        },
        "resources": resources,
    }
    kit_dir.mkdir(parents=True, exist_ok=True)
    (kit_dir / "manifest.toml").write_text(dumps(data), encoding="utf-8")


# ---------------------------------------------------------------------------
# Context: constraints loading via resource bindings
# ---------------------------------------------------------------------------

class TestContextConstraintsResourceBinding(unittest.TestCase):
    """Test that CypilotContext.load() uses resource binding for constraints path."""

    def test_constraints_loaded_from_binding_path(self):
        """When a 'constraints' resource binding exists and the file is present,
        context loads constraints from the binding path (not default kit root)."""
        from cypilot.utils.context import CypilotContext

        with TemporaryDirectory() as td:
            td_path = Path(td)
            root = td_path / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"

            # Create a custom constraints location (outside kit dir but
            # reachable from adapter_dir via '../')
            custom_dir = root / "custom" / "constraints"
            custom_dir.mkdir(parents=True)
            (custom_dir / "constraints.toml").write_text(
                '[artifacts]\n[artifacts.PRD]\nname = "PRD"\n[artifacts.PRD.identifiers]\n',
                encoding="utf-8",
            )

            # Kit dir with NO constraints.toml
            kit_dir = config / "kits" / "sdlc"
            kit_dir.mkdir(parents=True)

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
                            "constraints": {"path": "../custom/constraints/constraints.toml"},
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

            ctx = CypilotContext.load(root)
            self.assertIsNotNone(ctx)
            self.assertIn("sdlc", ctx.kits)
            # Constraints should be loaded (from custom path), not None
            self.assertIsNotNone(ctx.kits["sdlc"].constraints)

    def test_constraints_fallback_to_kit_root(self):
        """When no 'constraints' resource binding exists, constraints loaded from kit root."""
        from cypilot.utils.context import CypilotContext

        with TemporaryDirectory() as td:
            td_path = Path(td)
            root = td_path / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"

            kit_dir = config / "kits" / "sdlc"
            kit_dir.mkdir(parents=True)
            (kit_dir / "constraints.toml").write_text(
                '[artifacts]\n[artifacts.ADR]\nname = "ADR"\n[artifacts.ADR.identifiers]\n',
                encoding="utf-8",
            )

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

            ctx = CypilotContext.load(root)
            self.assertIsNotNone(ctx)
            self.assertIn("sdlc", ctx.kits)
            self.assertIsNotNone(ctx.kits["sdlc"].constraints)

    def test_binding_path_missing_file_falls_back(self):
        """When constraints binding path does not exist on disk, fall back to kit root."""
        from cypilot.utils.context import CypilotContext

        with TemporaryDirectory() as td:
            td_path = Path(td)
            root = td_path / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"

            kit_dir = config / "kits" / "sdlc"
            kit_dir.mkdir(parents=True)
            # Kit root has constraints
            (kit_dir / "constraints.toml").write_text("[artifacts]\n", encoding="utf-8")

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
                            "constraints": {"path": "nonexistent/constraints.toml"},
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

            ctx = CypilotContext.load(root)
            self.assertIsNotNone(ctx)
            self.assertIn("sdlc", ctx.kits)
            # Should still load (from kit root fallback), no crash
            self.assertIsNotNone(ctx.kits["sdlc"].constraints)


# ---------------------------------------------------------------------------
# validate-kits: resource path verification for registered kits
# ---------------------------------------------------------------------------

class TestValidateKitsResourcePaths(unittest.TestCase):
    """Test that run_validate_kits verifies resource paths for manifest-driven kits."""

    def test_missing_resource_path_produces_error(self):
        """Registered kit with resource binding pointing to missing path → FAIL."""
        from cypilot.utils.context import CypilotContext, set_context
        from cypilot.commands.validate_kits import run_validate_kits

        with TemporaryDirectory() as td:
            td_path = Path(td)
            root = td_path / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"

            kit_dir = config / "kits" / "sdlc"
            _write_minimal_constraints(kit_dir)

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

            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {"format": "Cypilot", "path": "config/kits/sdlc"},
                },
                "systems": [{"name": "Test", "slug": "test", "kit": "sdlc"}],
            }, config / "artifacts.toml")

            # constraints.toml exists but ADR dir does NOT
            # (constraints path exists because _write_minimal_constraints created it)

            ctx = CypilotContext.load(root)
            self.assertIsNotNone(ctx)
            set_context(ctx)

            try:
                rc, result = run_validate_kits(
                    project_root=ctx.project_root,
                    adapter_dir=ctx.adapter_dir,
                )
                # adr_artifacts path should be missing → error
                self.assertEqual(rc, 2)
                self.assertEqual(result["status"], "FAIL")
                self.assertGreater(result["error_count"], 0)
                # Check that the error mentions the missing resource
                errors = result.get("errors", [])
                resource_errors = [e for e in errors if e.get("type") == "resources"]
                self.assertGreater(len(resource_errors), 0)
                self.assertIn("adr_artifacts", resource_errors[0]["message"])
            finally:
                set_context(None)

    def test_all_resource_paths_exist_passes(self):
        """Registered kit with all resource bindings pointing to existing paths → PASS."""
        from cypilot.utils.context import CypilotContext, set_context
        from cypilot.commands.validate_kits import run_validate_kits

        with TemporaryDirectory() as td:
            td_path = Path(td)
            root = td_path / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"

            kit_dir = config / "kits" / "sdlc"
            _write_minimal_constraints(kit_dir)

            # Create the ADR artifacts directory so the path exists
            adr_dir = kit_dir / "artifacts" / "ADR"
            adr_dir.mkdir(parents=True)

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

            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {"format": "Cypilot", "path": "config/kits/sdlc"},
                },
                "systems": [{"name": "Test", "slug": "test", "kit": "sdlc"}],
            }, config / "artifacts.toml")

            ctx = CypilotContext.load(root)
            self.assertIsNotNone(ctx)
            set_context(ctx)

            try:
                rc, result = run_validate_kits(
                    project_root=ctx.project_root,
                    adapter_dir=ctx.adapter_dir,
                )
                self.assertEqual(rc, 0)
                self.assertEqual(result["status"], "PASS")
            finally:
                set_context(None)

    def test_legacy_kit_no_resource_check(self):
        """Legacy kit without resource bindings skips resource path verification."""
        from cypilot.utils.context import CypilotContext, set_context
        from cypilot.commands.validate_kits import run_validate_kits

        with TemporaryDirectory() as td:
            td_path = Path(td)
            root = td_path / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"

            kit_dir = config / "kits" / "sdlc"
            _write_minimal_constraints(kit_dir)

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

            ctx = CypilotContext.load(root)
            self.assertIsNotNone(ctx)
            set_context(ctx)

            try:
                rc, result = run_validate_kits(
                    project_root=ctx.project_root,
                    adapter_dir=ctx.adapter_dir,
                )
                self.assertEqual(rc, 0)
                self.assertEqual(result["status"], "PASS")
            finally:
                set_context(None)

    def test_verbose_report_uses_authoritative_adapter_relative_custom_root(self):
        from cypilot.utils.context import CypilotContext, set_context
        from cypilot.commands.validate_kits import run_validate_kits

        with TemporaryDirectory() as td:
            td_path = Path(td)
            root = td_path / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            custom_kit_dir = adapter / "custom-kits" / "sdlc"
            custom_kit_dir.mkdir(parents=True)
            (custom_kit_dir / "constraints.toml").write_text("[broken\ninvalid", encoding="utf-8")

            from cypilot.utils import toml_utils
            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {
                        "format": "Cypilot",
                        "path": "custom-kits/sdlc",
                        "version": "2.0",
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

            ctx = CypilotContext.load(root)
            self.assertIsNotNone(ctx)
            set_context(ctx)

            try:
                rc, result = run_validate_kits(
                    project_root=ctx.project_root,
                    adapter_dir=ctx.adapter_dir,
                    verbose=True,
                )
                self.assertEqual(rc, 2)
                self.assertEqual(result["status"], "FAIL")
                self.assertEqual(result["kits"][0]["path"], str(custom_kit_dir.resolve()))
                self.assertEqual(
                    result["kits"][0]["errors"][0]["path"],
                    str((custom_kit_dir / "constraints.toml").resolve()),
                )
            finally:
                set_context(None)


# ---------------------------------------------------------------------------
# validate-kits by path: manifest validation for standalone kits
# ---------------------------------------------------------------------------

class TestValidateKitByPathManifest(unittest.TestCase):
    """Test _validate_kit_by_path with manifest.toml validation."""

    def test_valid_manifest_passes(self):
        """Standalone kit with valid manifest.toml → no resource errors."""
        from cypilot.commands.validate_kits import _validate_kit_by_path

        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_dir = td_path / "mykit"
            kit_dir.mkdir()

            # Create constraints
            _write_minimal_constraints(kit_dir)

            # Create manifest with valid source paths
            (kit_dir / "artifacts").mkdir()
            (kit_dir / "artifacts" / "ADR").mkdir()
            _write_manifest_toml(kit_dir, [
                {
                    "id": "adr_artifacts",
                    "source": "artifacts/ADR",
                    "default_path": "artifacts/ADR",
                    "type": "directory",
                    "description": "ADR artifacts",
                },
            ])

            rc, result = _validate_kit_by_path(kit_dir)
            resource_errors = [
                e for e in result.get("errors", [])
                if e.get("type") == "resources"
            ]
            self.assertEqual(len(resource_errors), 0)

    def test_invalid_manifest_source_produces_error(self):
        """Standalone kit with manifest referencing missing source → error."""
        from cypilot.commands.validate_kits import _validate_kit_by_path

        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_dir = td_path / "mykit"
            kit_dir.mkdir()

            _write_minimal_constraints(kit_dir)

            # Manifest references source that does not exist
            _write_manifest_toml(kit_dir, [
                {
                    "id": "missing_resource",
                    "source": "nonexistent/dir",
                    "default_path": "some/path",
                    "type": "directory",
                    "description": "Missing resource",
                },
            ])

            rc, result = _validate_kit_by_path(kit_dir)
            resource_errors = [
                e for e in result.get("errors", [])
                if e.get("type") == "resources"
            ]
            self.assertGreater(len(resource_errors), 0)

    def test_no_manifest_no_resource_check(self):
        """Standalone kit without manifest.toml → no resource errors."""
        from cypilot.commands.validate_kits import _validate_kit_by_path

        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_dir = td_path / "mykit"
            kit_dir.mkdir()

            _write_minimal_constraints(kit_dir)

            rc, result = _validate_kit_by_path(kit_dir)
            resource_errors = [
                e for e in result.get("errors", [])
                if e.get("type") == "resources"
            ]
            self.assertEqual(len(resource_errors), 0)

    def test_malformed_manifest_produces_error(self):
        """Standalone kit with malformed manifest.toml → resource error reported."""
        from cypilot.commands.validate_kits import _validate_kit_by_path

        with TemporaryDirectory() as td:
            td_path = Path(td)
            kit_dir = td_path / "mykit"
            kit_dir.mkdir()

            _write_minimal_constraints(kit_dir)

            # Write malformed TOML
            (kit_dir / "manifest.toml").write_text("[broken\ninvalid", encoding="utf-8")

            rc, result = _validate_kit_by_path(kit_dir)
            resource_errors = [
                e for e in result.get("errors", [])
                if e.get("type") == "resources"
            ]
            self.assertGreater(len(resource_errors), 0)


# ---------------------------------------------------------------------------
# Kit filter respects resource checks
# ---------------------------------------------------------------------------

class TestValidateKitsFilterWithResources(unittest.TestCase):
    """Test that kit_filter applies to resource path verification."""

    def test_filter_skips_other_kit_resources(self):
        """With kit_filter, only the filtered kit's resources are verified."""
        from cypilot.utils.context import CypilotContext, set_context
        from cypilot.commands.validate_kits import run_validate_kits

        with TemporaryDirectory() as td:
            td_path = Path(td)
            root = td_path / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"

            # Kit "sdlc" with all paths present
            kit_dir = config / "kits" / "sdlc"
            _write_minimal_constraints(kit_dir)
            (kit_dir / "artifacts" / "ADR").mkdir(parents=True)

            # Kit "other" with missing resource path
            other_kit_dir = config / "kits" / "other"
            _write_minimal_constraints(other_kit_dir)

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
                    "other": {
                        "format": "Cypilot",
                        "path": "config/kits/other",
                        "version": "1.0",
                        "resources": {
                            "missing_thing": {"path": "nonexistent/path"},
                        },
                    },
                },
            }, config / "core.toml")

            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {"format": "Cypilot", "path": "config/kits/sdlc"},
                    "other": {"format": "Cypilot", "path": "config/kits/other"},
                },
                "systems": [{"name": "Test", "slug": "test", "kit": "sdlc"}],
            }, config / "artifacts.toml")

            ctx = CypilotContext.load(root)
            self.assertIsNotNone(ctx)
            set_context(ctx)

            try:
                # Filter to "sdlc" only — should PASS because sdlc paths exist
                rc, result = run_validate_kits(
                    project_root=ctx.project_root,
                    adapter_dir=ctx.adapter_dir,
                    kit_filter="sdlc",
                )
                self.assertEqual(rc, 0)
                self.assertEqual(result["status"], "PASS")
            finally:
                set_context(None)


class TestValidateCustomKitRootMetadata(unittest.TestCase):
    def setUp(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(True)

    def tearDown(self):
        from cypilot.utils.ui import set_json_mode
        set_json_mode(False)

    def test_cmd_validate_uses_authoritative_constraints_path_for_custom_root(self):
        from _test_helpers import write_constraints_toml
        from cypilot.commands.validate import cmd_validate
        from cypilot.utils.context import CypilotContext, set_context
        from cypilot.utils import toml_utils

        with TemporaryDirectory() as td:
            td_path = Path(td)
            root = td_path / "proj"
            adapter = _bootstrap_project(root)
            config = adapter / "config"
            custom_kit_dir = adapter / "custom-kits" / "sdlc"
            (custom_kit_dir / "artifacts" / "PRD").mkdir(parents=True, exist_ok=True)
            (custom_kit_dir / "artifacts" / "PRD" / "template.md").write_text("# PRD\n\n## Required Section\n", encoding="utf-8")
            write_constraints_toml(custom_kit_dir, {
                "PRD": {
                    "identifiers": {"fr": {"required": False}},
                    "headings": [
                        {"level": 1, "pattern": "PRD", "id": "prd-title"},
                        {"level": 2, "pattern": "Required Section", "id": "required-section"},
                    ],
                },
            })

            artifacts_dir = root / "architecture"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            artifact_path = artifacts_dir / "PRD.md"
            artifact_path.write_text("# PRD\n", encoding="utf-8")

            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {
                        "format": "Cypilot",
                        "path": "custom-kits/sdlc",
                        "version": "2.0",
                    },
                },
            }, config / "core.toml")

            toml_utils.dump({
                "version": "1.0",
                "project_root": "..",
                "kits": {
                    "sdlc": {"format": "Cypilot", "path": "config/kits/sdlc"},
                },
                "systems": [{
                    "name": "Test",
                    "slug": "test",
                    "kit": "sdlc",
                    "artifacts": [{
                        "path": "architecture/PRD.md",
                        "kind": "PRD",
                        "traceability": "FULL",
                    }],
                }],
            }, config / "artifacts.toml")

            ctx = CypilotContext.load(root)
            self.assertIsNotNone(ctx)
            set_context(ctx)

            try:
                buf = io.StringIO()
                with patch("cypilot.commands.validate_kits.run_validate_kits", return_value=(0, {"status": "PASS"})):
                    with redirect_stdout(buf):
                        rc = cmd_validate(["--skip-code"])
                self.assertEqual(rc, 2)
                out = json.loads(buf.getvalue())
                self.assertEqual(out["status"], "FAIL")
                self.assertTrue(any(
                    err.get("constraints_path") == str((custom_kit_dir / "constraints.toml").resolve())
                    for err in out.get("errors", [])
                ))
            finally:
                set_context(None)


if __name__ == "__main__":
    unittest.main()
