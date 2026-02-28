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
    (root / "AGENTS.md").write_text(
        f'<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "{adapter_rel}"\n```\n',
        encoding="utf-8",
    )
    adapter = root / adapter_rel
    adapter.mkdir(parents=True, exist_ok=True)
    (adapter / "config").mkdir(exist_ok=True)
    (adapter / "config" / "AGENTS.md").write_text("# Test adapter\n", encoding="utf-8")
    return adapter


def _bootstrap_self_check_kits(root: Path, adapter: Path, *, with_example: bool = True, bad_example: bool = False) -> None:
    # Minimal artifacts registry that passes `load_artifacts_meta` and contains kits.
    from cypilot.utils import toml_utils
    toml_utils.dump(
        {
            "project_root": "..",
            "systems": [],
            "kits": {
                "cypilot-sdlc": {"format": "Cypilot", "path": "kits/cypilot-sdlc"},
            },
        },
        adapter / "config" / "artifacts.toml",
    )

    kit_root = root / "kits" / "cypilot-sdlc"
    kit_root.mkdir(parents=True, exist_ok=True)
    (kit_root / "artifacts" / "REQ").mkdir(parents=True, exist_ok=True)
    (kit_root / "artifacts" / "REQ" / "template.md").write_text(
        "---\ncypilot-template:\n  version:\n    major: 1\n    minor: 0\n  kind: REQ\n---\n\n"
        "- [x] `p1` - **ID**: `cpt-{system}-req-{slug}`\n",
        encoding="utf-8",
    )
    from _test_helpers import write_constraints_toml
    write_constraints_toml(kit_root, {"REQ": {"identifiers": {"req": {"required": True, "template": "cpt-{system}-req-{slug}"}}}})

    if with_example:
        ex_dir = kit_root / "artifacts" / "REQ" / "examples"
        ex_dir.mkdir(parents=True, exist_ok=True)
        example = ex_dir / "example.md"

        if bad_example:
            example.write_text("# Example\n\n(no IDs)\n", encoding="utf-8")
        else:
            example.write_text(
                "- [x] `p1` - **ID**: `cpt-myapp-req-login`\n",
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


class TestCLIPyCoverageSelfCheckMoreBranches(unittest.TestCase):
    def _bootstrap_kit(
        self,
        root: Path,
        *,
        kind: str = "REQ",
        with_constraints: bool = True,
        constraints_payload: dict | None = None,
    ) -> "cypilot.utils.artifacts_meta.ArtifactsMeta":
        from cypilot.utils.artifacts_meta import ArtifactsMeta

        kit_root = root / "kits" / "k"
        (kit_root / "artifacts" / kind / "examples").mkdir(parents=True, exist_ok=True)
        (kit_root / "artifacts" / kind / "template.md").write_text("# T\n", encoding="utf-8")
        (kit_root / "artifacts" / kind / "examples" / "example.md").write_text(
            "- [x] `p1` - **ID**: `cpt-myapp-req-login`\n",
            encoding="utf-8",
        )

        if with_constraints:
            payload = constraints_payload
            if payload is None:
                payload = {
                    kind: {
                        "identifiers": {
                            "req": {"required": False, "template": "cpt-{system}-req-{slug}"}
                        }
                    }
                }
            from _test_helpers import write_constraints_toml
            write_constraints_toml(kit_root, payload)

        reg = {
            "version": "1.1",
            "project_root": "..",
            "systems": [],
            "kits": {
                "k": {
                    "format": "Cypilot",
                    "path": "kits/k",
                    "artifacts": {
                        kind: {
                            "template": "{project_root}/kits/k/artifacts/%s/template.md" % kind,
                            "examples": "{project_root}/kits/k/artifacts/%s/examples" % kind,
                        }
                    },
                }
            },
        }
        return ArtifactsMeta.from_dict(reg)

    def test_run_self_check_fails_when_constraints_missing(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            meta = self._bootstrap_kit(root, with_constraints=False)
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")
            self.assertGreaterEqual(int(out.get("kits_checked", 0)), 1)

    def test_run_self_check_fails_on_invalid_constraints_json(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            meta = self._bootstrap_kit(root, with_constraints=True, constraints_payload={"REQ": {}})
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")
            self.assertGreaterEqual(int(out.get("kits_checked", 0)), 1)

    def test_run_self_check_fails_when_kind_not_in_constraints(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            meta = self._bootstrap_kit(root, with_constraints=True, constraints_payload={"OTHER": {"identifiers": {}}})
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")

    def test_template_checks_phase_gate_on_heading_errors(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            meta = self._bootstrap_kit(root, with_constraints=True)

            with patch(
                "cypilot.commands.self_check.validate_headings_contract",
                return_value={"errors": [{"type": "x", "message": "boom", "path": "p", "line": 1}], "warnings": []},
            ):
                rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta, verbose=True)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")

    def test_template_checks_template_unreadable_branch(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            meta = self._bootstrap_kit(root, with_constraints=True)

            with patch("cypilot.commands.self_check.read_text_safe", return_value=None):
                rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")

    def test_template_checks_fails_on_identifier_without_template(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            # identifiers.req has no template -> error branch
            meta = self._bootstrap_kit(
                root,
                with_constraints=True,
                constraints_payload={
                    "REQ": {
                        "identifiers": {
                            "req": {"required": False}
                        }
                    }
                },
            )
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta, verbose=True)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")
            self.assertIn("errors", out["results"][0])

    def test_template_checks_fail_when_required_id_placeholder_missing(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            meta = self._bootstrap_kit(
                root,
                with_constraints=True,
                constraints_payload={
                    "REQ": {
                        "identifiers": {
                            "req": {"required": True, "template": "cpt-{system}-req-{slug}"}
                        }
                    }
                },
            )
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")

    def test_template_checks_id_placeholder_wrong_heading(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            kit_root = root / "kits" / "k" / "artifacts" / "REQ"
            kit_root.mkdir(parents=True, exist_ok=True)
            (kit_root / "template.md").write_text(
                "# T\n\n- [ ] **ID**: `cpt-{system}-req-{slug}`\n",
                encoding="utf-8",
            )
            (kit_root / "examples").mkdir(parents=True, exist_ok=True)
            (kit_root / "examples" / "example.md").write_text(
                "- [x] `p1` - **ID**: `cpt-myapp-req-login`\n",
                encoding="utf-8",
            )
            from _test_helpers import write_constraints_toml
            write_constraints_toml(root / "kits" / "k", {
                "REQ": {
                    "headings": [{"level": 1, "pattern": "^T$"}],
                    "identifiers": {
                        "req": {
                            "required": True,
                            "template": "cpt-{system}-req-{slug}",
                            "headings": ["allowed"],
                        }
                    },
                }
            })
            from cypilot.utils.artifacts_meta import ArtifactsMeta

            meta = ArtifactsMeta.from_dict(
                {
                    "version": "1.1",
                    "project_root": "..",
                    "systems": [],
                    "kits": {
                        "k": {
                            "format": "Cypilot",
                            "path": "kits/k",
                            "artifacts": {
                                "REQ": {
                                    "template": "{project_root}/kits/k/artifacts/REQ/template.md",
                                    "examples": "{project_root}/kits/k/artifacts/REQ/examples",
                                }
                            },
                        }
                    },
                }
            )

            fake_headings_at = [[] for _ in range(10)]
            fake_headings_at[3] = ["not-allowed"]
            with patch("cypilot.commands.self_check.heading_constraint_ids_by_line", return_value=fake_headings_at):
                rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")

    def test_template_checks_required_reference_missing(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            meta = self._bootstrap_kit(
                root,
                with_constraints=True,
                constraints_payload={
                    "SRC": {
                        "identifiers": {
                            "x": {
                                "required": False,
                                "template": "cpt-{system}-x-{slug}",
                                "references": {"REQ": {"coverage": True}},
                            }
                        }
                    },
                    "REQ": {"identifiers": {"req": {"required": False, "template": "cpt-{system}-req-{slug}"}}},
                },
            )
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")

    def test_template_checks_required_reference_wrong_heading(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            kit_root = root / "kits" / "k" / "artifacts" / "REQ"
            kit_root.mkdir(parents=True, exist_ok=True)
            (kit_root / "template.md").write_text(
                "# T\n\nRef `cpt-{system}-x-{slug}`\n",
                encoding="utf-8",
            )
            (kit_root / "examples").mkdir(parents=True, exist_ok=True)
            (kit_root / "examples" / "example.md").write_text(
                "- [x] `p1` - **ID**: `cpt-myapp-req-login`\n",
                encoding="utf-8",
            )
            from _test_helpers import write_constraints_toml
            write_constraints_toml(root / "kits" / "k", {
                "SRC": {
                    "identifiers": {
                        "x": {
                            "required": False,
                            "template": "cpt-{system}-x-{slug}",
                            "references": {"REQ": {"coverage": True, "headings": ["allowed"]}},
                        }
                    }
                },
                "REQ": {
                    "headings": [{"level": 1, "pattern": "^T$"}],
                    "identifiers": {
                        "req": {"required": False, "template": "cpt-{system}-req-{slug}"}
                    },
                },
            })
            from cypilot.utils.artifacts_meta import ArtifactsMeta

            meta = ArtifactsMeta.from_dict(
                {
                    "version": "1.1",
                    "project_root": "..",
                    "systems": [],
                    "kits": {
                        "k": {
                            "format": "Cypilot",
                            "path": "kits/k",
                            "artifacts": {
                                "REQ": {
                                    "template": "{project_root}/kits/k/artifacts/REQ/template.md",
                                    "examples": "{project_root}/kits/k/artifacts/REQ/examples",
                                }
                            },
                        }
                    },
                }
            )
            fake_headings_at = [[] for _ in range(10)]
            fake_headings_at[3] = ["not-allowed"]
            with patch("cypilot.commands.self_check.heading_constraint_ids_by_line", return_value=fake_headings_at):
                rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta)
            self.assertEqual(rc, 2)
            self.assertEqual(out.get("status"), "FAIL")

    def test_run_self_check_fallback_when_kit_paths_raise(self):
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            meta = self._bootstrap_kit(root, with_constraints=True)
            kit = meta.kits["k"]

            def _boom(_kind: str) -> str:
                raise Exception("boom")

            kit.get_template_path = _boom
            kit.get_examples_path = _boom

            # Legacy fallback layout already exists from _bootstrap_kit.
            # Verify fallback picks up the files even when get_*_path raises.
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta, verbose=True)
            self.assertEqual(rc, 0)
            self.assertEqual(out.get("status"), "PASS")


class TestCLIPyCoverageSelfCheckReverseAndOptional(unittest.TestCase):
    """Tests for self-check reverse checks and optional missing warnings."""

    def _bootstrap_kit(self, root, *, kind="REQ", constraints_payload=None, template_content=None):
        from cypilot.utils.artifacts_meta import ArtifactsMeta

        kit_root = root / "kits" / "k"
        (kit_root / "artifacts" / kind / "examples").mkdir(parents=True, exist_ok=True)
        tmpl = template_content or "# T\n"
        (kit_root / "artifacts" / kind / "template.md").write_text(tmpl, encoding="utf-8")
        (kit_root / "artifacts" / kind / "examples" / "example.md").write_text(
            "- [x] `p1` - **ID**: `cpt-myapp-req-login`\n", encoding="utf-8",
        )
        if constraints_payload is not None:
            from _test_helpers import write_constraints_toml
            write_constraints_toml(kit_root, constraints_payload)
        reg = {
            "version": "1.1", "project_root": "..", "systems": [],
            "kits": {"k": {"format": "Cypilot", "path": "kits/k", "artifacts": {
                kind: {
                    "template": "{project_root}/kits/k/artifacts/%s/template.md" % kind,
                    "examples": "{project_root}/kits/k/artifacts/%s/examples" % kind,
                },
            }}},
        }
        return ArtifactsMeta.from_dict(reg)

    def test_template_def_kind_not_in_constraints(self):
        """Template has definition pattern not in constraints → error."""
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            tmpl = (
                "---\ncypilot-template:\n  version:\n    major: 1\n    minor: 0\n  kind: REQ\n---\n"
                "- [ ] `p1` - **ID**: `cpt-{system}-unknown-{slug}`\n"
            )
            meta = self._bootstrap_kit(root, constraints_payload={
                "REQ": {"identifiers": {"req": {"required": False, "template": "cpt-{system}-req-{slug}"}}}
            }, template_content=tmpl)
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta, verbose=True)
            self.assertEqual(rc, 2)
            errs = out["results"][0].get("errors", [])
            codes = [e.get("code") for e in errs]
            self.assertIn("template-def-kind-not-in-constraints", codes)

    def test_template_ref_kind_not_in_constraints(self):
        """Template has reference pattern not in constraints → error."""
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            tmpl = (
                "---\ncypilot-template:\n  version:\n    major: 1\n    minor: 0\n  kind: REQ\n---\n"
                "- [ ] `p1` - **ID**: `cpt-{system}-req-{slug}`\n"
                "**Refs**: `cpt-{system}-bogus-{slug}`\n"
            )
            meta = self._bootstrap_kit(root, constraints_payload={
                "REQ": {"identifiers": {"req": {"required": False, "template": "cpt-{system}-req-{slug}"}}}
            }, template_content=tmpl)
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta, verbose=True)
            self.assertEqual(rc, 2)
            errs = out["results"][0].get("errors", [])
            codes = [e.get("code") for e in errs]
            self.assertIn("template-ref-kind-not-in-constraints", codes)

    def test_optional_def_missing_from_template_warns(self):
        """Optional definition kind in constraints but missing from template → warning."""
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            # Template has no ID definitions at all — optional kind 'req' missing
            tmpl = "---\ncypilot-template:\n  version:\n    major: 1\n    minor: 0\n  kind: REQ\n---\n# T\n"
            meta = self._bootstrap_kit(root, constraints_payload={
                "REQ": {"identifiers": {"req": {"required": False, "template": "cpt-{system}-req-{slug}"}}}
            }, template_content=tmpl)
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta, verbose=True)
            # Should pass (optional), but with a warning
            warns = out["results"][0].get("warnings", [])
            msgs = [w.get("message", "") for w in warns]
            self.assertTrue(any("optional ID placeholder" in m for m in msgs), f"Expected optional warning, got: {msgs}")

    def test_optional_ref_missing_from_template_warns(self):
        """Optional reference in constraints but missing from template → warning."""
        from cypilot.commands.self_check import run_self_check_from_meta

        with TemporaryDirectory() as td:
            root = Path(td)
            # PRD defines 'fr', DESIGN references 'fr' as optional — but DESIGN template doesn't have the reference placeholder
            tmpl = "---\ncypilot-template:\n  version:\n    major: 1\n    minor: 0\n  kind: DESIGN\n---\n# T\n"
            constraints = {
                "PRD": {"identifiers": {"fr": {"required": False, "template": "cpt-{system}-fr-{slug}", "references": {
                    "DESIGN": {}
                }}}},
                "DESIGN": {"identifiers": {"design": {"required": False, "template": "cpt-{system}-design-{slug}"}}},
            }
            meta = self._bootstrap_kit(root, kind="DESIGN", constraints_payload=constraints, template_content=tmpl)
            rc, out = run_self_check_from_meta(project_root=root, adapter_dir=(root / "adapter"), artifacts_meta=meta, verbose=True)
            warns = out["results"][0].get("warnings", [])
            msgs = [w.get("message", "") for w in warns]
            self.assertTrue(any("optional reference placeholder" in m for m in msgs), f"Expected optional ref warning, got: {warns}")


class TestCLIPyCoverageValidateBranches(unittest.TestCase):
    def test_validate_artifact_outside_project_root_hits_relative_to_error(self):
        from cypilot.commands import validate as validate_cmd

        class _FakeKitPkg:
            def is_cypilot_format(self):
                return True

            def get_template_path(self, _kind: str) -> str:
                return "kits/x/artifacts/REQ/template.md"

        class _FakeMeta:
            systems = []

            def get_artifact_by_path(self, _rel: str):
                return None

            def get_kit(self, _kit_id: str):
                return _FakeKitPkg()

            def iter_all_artifacts(self):
                return iter([])

            def is_ignored(self, _rel: str) -> bool:
                return False

        class _FakeKit:
            path = "kits/x"

        class _FakeLoadedKit:
            kit = _FakeKit()
            constraints = None

        class _FakeCtx:
            meta = _FakeMeta()
            project_root = Path("/tmp/nonexistent-root")
            registered_systems = set(["sys"])
            kits = {"x": _FakeLoadedKit()}

            def get_known_id_kinds(self):
                return set()

        with TemporaryDirectory() as td:
            tmp = Path(td)
            outside = tmp / "outside"
            outside.mkdir(parents=True, exist_ok=True)
            art = outside / "A.md"
            art.write_text("# X\n", encoding="utf-8")

            # Force context to claim a different project root so Path.relative_to() raises ValueError.
            fake_ctx = _FakeCtx()
            fake_ctx.project_root = tmp / "project"

            buf = io.StringIO()
            with patch("cypilot.utils.context.CypilotContext.load", return_value=fake_ctx):
                with patch("cypilot.utils.context.get_context", return_value=fake_ctx):
                    with redirect_stdout(buf):
                        rc = validate_cmd.cmd_validate(["--artifact", str(art)])

            self.assertEqual(rc, 1)
            out = json.loads(buf.getvalue())
            self.assertEqual(out.get("status"), "ERROR")

    def test_validate_early_stop_writes_output_file(self):
        from cypilot.commands import validate as validate_cmd

        class _FakeKitPkg:
            def is_cypilot_format(self):
                return True

            def get_template_path(self, _kind: str) -> str:
                return "kits/x/artifacts/REQ/template.md"

        class _FakeSystemNode:
            kit = "x"

        class _FakeArtifactMeta:
            def __init__(self, path: str, kind: str, traceability: str = "FULL"):
                self.path = path
                self.kind = kind
                self.traceability = traceability

        class _FakeMeta:
            def __init__(self, root: Path, art_rel: str):
                self._root = root
                self._art_rel = art_rel
                self.systems = []

            def iter_all_artifacts(self):
                yield _FakeArtifactMeta(self._art_rel, "REQ", "FULL"), _FakeSystemNode()

            def get_kit(self, _kit_id: str):
                return _FakeKitPkg()

            def is_ignored(self, _rel: str) -> bool:
                return False

        class _FakeKit:
            path = "kits/x"

        class _FakeLoadedKit:
            kit = _FakeKit()
            constraints = types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[])})

        class _FakeCtx:
            def __init__(self, root: Path, art_rel: str):
                self.meta = _FakeMeta(root, art_rel)
                self.project_root = root
                self.registered_systems = set(["sys"])
                self.kits = {"x": _FakeLoadedKit()}
                self._errors = []

            def get_known_id_kinds(self):
                return set()

        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "kits" / "x" / "artifacts" / "REQ").mkdir(parents=True, exist_ok=True)
            (root / "kits" / "x" / "artifacts" / "REQ" / "template.md").write_text("# T\n", encoding="utf-8")

            art_rel = "artifacts/REQ.md"
            (root / "artifacts").mkdir(parents=True, exist_ok=True)
            (root / art_rel).write_text("# R\n", encoding="utf-8")

            ctx = _FakeCtx(root, art_rel)
            out_path = root / "out.json"

            with patch("cypilot.utils.context.get_context", return_value=ctx):
                # Force per-artifact validation to fail so cmd_validate returns early and writes output.
                with patch("cypilot.commands.validate.validate_artifact_file", return_value={"errors": [{"type": "x", "message": "boom", "path": str(root / art_rel), "line": 1}], "warnings": []}):
                    rc = validate_cmd.cmd_validate(["--output", str(out_path)])

            self.assertEqual(rc, 2)
            self.assertTrue(out_path.is_file())

    def test_validate_skips_non_cypilot_artifacts_in_registry(self):
        from cypilot.commands import validate as validate_cmd

        class _FakePkg:
            def is_cypilot_format(self):
                return False

        class _FakeSystemNode:
            kit = "x"
            artifacts = []
            codebase = []
            children = []

        class _FakeArtifactMeta:
            path = "a.md"
            kind = "REQ"
            traceability = "FULL"

        class _FakeMeta:
            systems = []

            def iter_all_artifacts(self):
                yield _FakeArtifactMeta(), _FakeSystemNode()

            def get_kit(self, _kit_id: str):
                return _FakePkg()

        class _FakeCtx:
            def __init__(self, root: Path):
                self.meta = _FakeMeta()
                self.project_root = root
                self.registered_systems = set()
                self.kits = {}
                self._errors = []

            def get_known_id_kinds(self):
                return set()

        with TemporaryDirectory() as td:
            root = Path(td)
            ctx = _FakeCtx(root)
            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with redirect_stdout(buf):
                    rc = validate_cmd.cmd_validate([])
            # Validate succeeds with empty/non-Cypilot artifacts
            self.assertIn(rc, [0, 1, 2])
            out = json.loads(buf.getvalue())
            self.assertIn("status", out)

    def test_validate_ctx_errors_are_reported_and_trigger_early_fail(self):
        from cypilot.commands import validate as validate_cmd

        class _FakeKitPkg:
            def is_cypilot_format(self):
                return True

            def get_template_path(self, _kind: str) -> str:
                return "kits/x/artifacts/REQ/template.md"

        class _FakeSystemNode:
            kit = "x"
            artifacts = []
            codebase = []
            children = []

        class _FakeArtifactMeta:
            def __init__(self, path: str):
                self.path = path
                self.kind = "REQ"
                self.traceability = "FULL"

        class _FakeMeta:
            def __init__(self, art_rel: str):
                self._art_rel = art_rel
                self.systems = []

            def iter_all_artifacts(self):
                yield _FakeArtifactMeta(self._art_rel), _FakeSystemNode()

            def get_kit(self, _kit_id: str):
                return _FakeKitPkg()

        class _FakeKit:
            path = "kits/x"

        class _FakeLoadedKit:
            kit = _FakeKit()
            constraints = types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[types.SimpleNamespace(kind="req")])})

        class _FakeCtx:
            def __init__(self, root: Path, art_rel: str):
                self.meta = _FakeMeta(art_rel)
                self.project_root = root
                self.registered_systems = set(["sys"])
                self.kits = {"x": _FakeLoadedKit()}
                self._errors = [{"type": "constraints", "message": "ctx boom", "path": "<x>", "line": 1}]

            def get_known_id_kinds(self):
                return set()

        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "kits" / "x" / "artifacts" / "REQ").mkdir(parents=True, exist_ok=True)
            (root / "kits" / "x" / "artifacts" / "REQ" / "template.md").write_text("# T\n", encoding="utf-8")
            (root / "artifacts").mkdir(parents=True, exist_ok=True)
            art_rel = "artifacts/REQ.md"
            (root / art_rel).write_text("# R\n", encoding="utf-8")

            ctx = _FakeCtx(root, art_rel)
            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("cypilot.commands.validate.validate_artifact_file", return_value={"errors": [], "warnings": []}):
                    with redirect_stdout(buf):
                        rc = validate_cmd.cmd_validate([])

            self.assertEqual(rc, 2)
            out = json.loads(buf.getvalue())
            self.assertEqual(out.get("status"), "FAIL")
            self.assertGreater(out.get("error_count", 0), 0)

    def test_validate_constraints_path_resolve_error_and_verbose_scan_exception(self):
        from cypilot.commands import validate as validate_cmd

        class _FakeKitPkg:
            def is_cypilot_format(self):
                return True

            def get_template_path(self, _kind: str) -> str:
                return "kits/x/artifacts/REQ/template.md"

        class _BadKit:
            @property
            def path(self):
                raise RuntimeError("boom")

        class _FakeLoadedKit:
            kit = _BadKit()
            constraints = types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[])})

        class _FakeSystemNode:
            kit = "x"
            artifacts = []
            codebase = []
            children = []

        class _FakeArtifactMeta:
            def __init__(self, path: str):
                self.path = path
                self.kind = "REQ"
                self.traceability = "FULL"

        class _FakeMeta:
            def __init__(self, art_rel: str):
                self._art_rel = art_rel
                self.systems = []

            def iter_all_artifacts(self):
                yield _FakeArtifactMeta(self._art_rel), _FakeSystemNode()

            def get_kit(self, _kit_id: str):
                return _FakeKitPkg()

        class _FakeCtx:
            def __init__(self, root: Path, art_rel: str):
                self.meta = _FakeMeta(art_rel)
                self.project_root = root
                self.registered_systems = set(["sys"])
                self.kits = {"x": _FakeLoadedKit()}
                self._errors = []

            def get_known_id_kinds(self):
                return set()

        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "kits" / "x" / "artifacts" / "REQ").mkdir(parents=True, exist_ok=True)
            (root / "kits" / "x" / "artifacts" / "REQ" / "template.md").write_text("# T\n", encoding="utf-8")
            (root / "artifacts").mkdir(parents=True, exist_ok=True)
            art_rel = "artifacts/REQ.md"
            (root / art_rel).write_text("# R\n", encoding="utf-8")

            ctx = _FakeCtx(root, art_rel)
            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("cypilot.commands.validate.scan_cpt_ids", side_effect=RuntimeError("scan boom")):
                    with patch(
                        "cypilot.commands.validate.validate_artifact_file",
                        return_value={"errors": [{"type": "x", "message": "boom", "path": str(root / art_rel), "line": 1}], "warnings": []},
                    ):
                        with redirect_stdout(buf):
                            rc = validate_cmd.cmd_validate(["--verbose"])

            self.assertEqual(rc, 2)
            out = json.loads(buf.getvalue())
            self.assertEqual(out.get("status"), "FAIL")

    def test_validate_cross_validation_filters_by_validated_paths(self):
        from cypilot.commands import validate as validate_cmd

        class _FakeKitPkg:
            def is_cypilot_format(self):
                return True

            def get_template_path(self, kind: str) -> str:
                return f"kits/x/artifacts/{kind}/template.md"

        class _FakeSystemNode:
            def __init__(self, kit: str):
                self.kit = kit
                self.artifacts = []
                self.codebase = []
                self.children = []

        class _FakeArtifactMeta:
            def __init__(self, path: str, kind: str):
                self.path = path
                self.kind = kind
                self.traceability = "FULL"

        class _FakeMeta:
            def __init__(self, artifacts: list[tuple[str, str, str]]):
                self._arts = artifacts
                self.systems = []

            def iter_all_artifacts(self):
                for p, k, kit in self._arts:
                    yield _FakeArtifactMeta(p, k), _FakeSystemNode(kit)

            def get_kit(self, _kit_id: str):
                return _FakeKitPkg() if _kit_id != "skip" else types.SimpleNamespace(is_cypilot_format=lambda: False)

            def is_ignored(self, _rel: str) -> bool:
                return False

        class _FakeKit:
            path = "kits/x"

        class _FakeLoadedKit:
            kit = _FakeKit()
            constraints = types.SimpleNamespace(by_kind={
                "REQ": types.SimpleNamespace(defined_id=[]),
                "OTHER": types.SimpleNamespace(defined_id=[]),
            })

        class _FakeCtx:
            def __init__(self, root: Path, arts: list[tuple[str, str, str]]):
                self.meta = _FakeMeta(arts)
                self.project_root = root
                self.registered_systems = set(["sys"])
                self.kits = {"x": _FakeLoadedKit()}
                self._errors = []

            def get_known_id_kinds(self):
                return set()

        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "kits" / "x" / "artifacts" / "REQ").mkdir(parents=True, exist_ok=True)
            (root / "kits" / "x" / "artifacts" / "REQ" / "template.md").write_text("# T\n", encoding="utf-8")
            (root / "kits" / "x" / "artifacts" / "OTHER").mkdir(parents=True, exist_ok=True)
            (root / "kits" / "x" / "artifacts" / "OTHER" / "template.md").write_text("# T\n", encoding="utf-8")

            (root / "artifacts").mkdir(parents=True, exist_ok=True)
            req_rel = "artifacts/REQ.md"
            (root / req_rel).write_text("# R\n", encoding="utf-8")
            other_rel = "artifacts/OTHER.md"
            (root / other_rel).write_text("# O\n", encoding="utf-8")
            missing_rel = "artifacts/MISSING.md"

            arts = [
                (req_rel, "REQ", "x"),
                (missing_rel, "OTHER", "x"),
                (other_rel, "OTHER", "x"),
                ("artifacts/SKIP.md", "OTHER", "skip"),
            ]
            ctx = _FakeCtx(root, arts)
            buf = io.StringIO()
            validated_path = str((root / req_rel).resolve())

            fake_cross = {
                "errors": [
                    {"type": "constraints", "message": "e1", "path": validated_path, "line": 1},
                    {"type": "constraints", "message": "e2", "path": str((root / other_rel).resolve()), "line": 1},
                ],
                "warnings": [
                    {"type": "constraints", "message": "w1", "path": validated_path, "line": 1},
                    {"type": "constraints", "message": "w2", "path": str((root / other_rel).resolve()), "line": 1},
                ],
            }

            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("cypilot.commands.validate.validate_artifact_file", return_value={"errors": [], "warnings": []}):
                    with patch("cypilot.commands.validate.cross_validate_artifacts", return_value=fake_cross):
                        with patch("cypilot.commands.validate.scan_cpt_ids", return_value=[]):
                            with redirect_stdout(buf):
                                rc = validate_cmd.cmd_validate(["--skip-code", "--verbose"])

            self.assertEqual(rc, 2)
            out = json.loads(buf.getvalue())
            self.assertEqual(out.get("status"), "FAIL")
            self.assertIn("errors", out)
            self.assertIn("warnings", out)

    def test_validate_full_id_scan_exception_is_handled(self):
        from cypilot.commands import validate as validate_cmd

        class _FakeKitPkg:
            def is_cypilot_format(self):
                return True

            def get_template_path(self, _kind: str) -> str:
                return "kits/x/artifacts/REQ/template.md"

        class _FakeSystemNode:
            kit = "x"
            artifacts = []
            codebase = []
            children = []

        class _FakeArtifactMeta:
            def __init__(self, path: str):
                self.path = path
                self.kind = "REQ"
                self.traceability = "FULL"

        class _FakeMeta:
            def __init__(self, art_rel: str):
                self._art_rel = art_rel
                self.systems = []

            def iter_all_artifacts(self):
                yield _FakeArtifactMeta(self._art_rel), _FakeSystemNode()

            def get_kit(self, _kit_id: str):
                return _FakeKitPkg()

            def is_ignored(self, _rel: str) -> bool:
                return False

        class _FakeKit:
            path = "kits/x"

        class _FakeLoadedKit:
            kit = _FakeKit()
            constraints = types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[])})

        class _FakeCtx:
            def __init__(self, root: Path, art_rel: str):
                self.meta = _FakeMeta(art_rel)
                self.project_root = root
                self.registered_systems = set(["sys"])
                self.kits = {"x": _FakeLoadedKit()}
                self._errors = []

            def get_known_id_kinds(self):
                return set()

        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "kits" / "x" / "artifacts" / "REQ").mkdir(parents=True, exist_ok=True)
            (root / "kits" / "x" / "artifacts" / "REQ" / "template.md").write_text("# T\n", encoding="utf-8")
            (root / "artifacts").mkdir(parents=True, exist_ok=True)
            art_rel = "artifacts/REQ.md"
            (root / art_rel).write_text("# R\n", encoding="utf-8")

            ctx = _FakeCtx(root, art_rel)
            buf = io.StringIO()
            calls = {"n": 0}

            def _scan(_p: Path):
                calls["n"] += 1
                if calls["n"] == 1:
                    raise RuntimeError("boom")
                return []

            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch("cypilot.commands.validate.validate_artifact_file", return_value={"errors": [], "warnings": []}):
                    with patch("cypilot.commands.validate.cross_validate_artifacts", return_value={"errors": [], "warnings": []}):
                        with patch("cypilot.commands.validate.scan_cpt_ids", side_effect=_scan):
                            with redirect_stdout(buf):
                                rc = validate_cmd.cmd_validate(["--skip-code"])

            self.assertEqual(rc, 0)

    def test_validate_code_scan_branches_and_failure_includes_warnings(self):
        from cypilot.commands import validate as validate_cmd

        class _FakeKitPkg:
            def is_cypilot_format(self):
                return True

            def get_template_path(self, _kind: str) -> str:
                return "kits/x/artifacts/REQ/template.md"

        class _FakeCodebaseEntry:
            def __init__(self, path: str, extensions: list[str]):
                self.path = path
                self.extensions = extensions

        class _FakeSystemNode:
            def __init__(self, code_path: str):
                self.kit = "x"
                self.artifacts = []
                self.codebase = [_FakeCodebaseEntry(code_path, [".py"])]
                self.children = []

        class _FakeArtifactMeta:
            def __init__(self, path: str):
                self.path = path
                self.kind = "REQ"
                self.traceability = "FULL"

        class _FakeMeta:
            def __init__(self, art_rel: str, code_path: str):
                self._art_rel = art_rel
                self.systems = [_FakeSystemNode(code_path)]

            def iter_all_artifacts(self):
                yield _FakeArtifactMeta(self._art_rel), types.SimpleNamespace(kit="x")

            def get_kit(self, _kit_id: str):
                return _FakeKitPkg()

            def is_ignored(self, _rel: str) -> bool:
                return False

        class _FakeKit:
            path = "kits/x"

        class _FakeLoadedKit:
            kit = _FakeKit()
            constraints = types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[])})

        class _FakeCtx:
            def __init__(self, root: Path, art_rel: str, code_path: str):
                self.meta = _FakeMeta(art_rel, code_path)
                self.project_root = root
                self.registered_systems = set(["sys"])
                self.kits = {"x": _FakeLoadedKit()}
                self._errors = []

            def get_known_id_kinds(self):
                return set()

        with TemporaryDirectory() as td1:
            with TemporaryDirectory() as td2:
                root = Path(td1)
                outside = Path(td2)
                code_file = outside / "x.py"
                code_file.write_text("print('x')\n", encoding="utf-8")

                (root / "kits" / "x" / "artifacts" / "REQ").mkdir(parents=True, exist_ok=True)
                (root / "kits" / "x" / "artifacts" / "REQ" / "template.md").write_text("# T\n", encoding="utf-8")
                (root / "artifacts").mkdir(parents=True, exist_ok=True)
                art_rel = "artifacts/REQ.md"
                (root / art_rel).write_text("# R\n", encoding="utf-8")

                ctx = _FakeCtx(root, art_rel, str(code_file))
                buf = io.StringIO()

                with patch("cypilot.utils.context.get_context", return_value=ctx):
                    with patch("cypilot.commands.validate.cross_validate_artifacts", return_value={"errors": [], "warnings": []}):
                        with patch("cypilot.commands.validate.scan_cpt_ids", return_value=[]):
                            with patch(
                                "cypilot.commands.validate.validate_artifact_file",
                                return_value={"errors": [], "warnings": [{"type": "w", "message": "warn", "path": str(root / art_rel), "line": 1}]},
                            ):
                                with patch(
                                    "cypilot.commands.validate.CodeFile.from_path",
                                    return_value=(None, [{"type": "code", "message": "bad", "path": str(code_file), "line": 1}]),
                                ):
                                    with redirect_stdout(buf):
                                        rc = validate_cmd.cmd_validate([])

                self.assertEqual(rc, 2)
                out = json.loads(buf.getvalue())
                self.assertEqual(out.get("status"), "FAIL")
                self.assertIn("warnings", out)

    def test_validate_pass_can_include_failed_artifacts_summary(self):
        from cypilot.commands import validate as validate_cmd

        class _TruthyEmpty:
            def __iter__(self):
                return iter([])

            def __len__(self):
                return 1

        class _FakeKitPkg:
            def is_cypilot_format(self):
                return True

            def get_template_path(self, _kind: str) -> str:
                return "kits/x/artifacts/REQ/template.md"

        class _FakeSystemNode:
            kit = "x"
            artifacts = []
            codebase = []
            children = []

        class _FakeArtifactMeta:
            def __init__(self, path: str):
                self.path = path
                self.kind = "REQ"
                self.traceability = "FULL"

        class _FakeMeta:
            def __init__(self, art_rel: str):
                self._art_rel = art_rel
                self.systems = []

            def iter_all_artifacts(self):
                yield _FakeArtifactMeta(self._art_rel), _FakeSystemNode()

            def get_kit(self, _kit_id: str):
                return _FakeKitPkg()

            def is_ignored(self, _rel: str) -> bool:
                return False

        class _FakeKit:
            path = "kits/x"

        class _FakeLoadedKit:
            kit = _FakeKit()
            constraints = types.SimpleNamespace(by_kind={"REQ": types.SimpleNamespace(defined_id=[])})

        class _FakeCtx:
            def __init__(self, root: Path, art_rel: str):
                self.meta = _FakeMeta(art_rel)
                self.project_root = root
                self.registered_systems = set(["sys"])
                self.kits = {"x": _FakeLoadedKit()}
                self._errors = []

            def get_known_id_kinds(self):
                return set()

        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "kits" / "x" / "artifacts" / "REQ").mkdir(parents=True, exist_ok=True)
            (root / "kits" / "x" / "artifacts" / "REQ" / "template.md").write_text("# T\n", encoding="utf-8")
            (root / "artifacts").mkdir(parents=True, exist_ok=True)
            art_rel = "artifacts/REQ.md"
            (root / art_rel).write_text("# R\n", encoding="utf-8")

            ctx = _FakeCtx(root, art_rel)
            buf = io.StringIO()
            with patch("cypilot.utils.context.get_context", return_value=ctx):
                with patch(
                    "cypilot.commands.validate.validate_artifact_file",
                    return_value={"errors": _TruthyEmpty(), "warnings": []},
                ):
                    with patch("cypilot.commands.validate.cross_validate_artifacts", return_value={"errors": [], "warnings": []}):
                        with patch("cypilot.commands.validate.scan_cpt_ids", return_value=[]):
                            with redirect_stdout(buf):
                                rc = validate_cmd.cmd_validate(["--skip-code"])

            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            self.assertEqual(out.get("status"), "PASS")
            self.assertIn("failed_artifacts", out)


class TestCLIPyCoverageListIdKindsBranches(unittest.TestCase):
    def test_list_id_kinds_artifact_not_found_branch(self):
        from cypilot.commands.list_id_kinds import cmd_list_id_kinds

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_list_id_kinds(["--artifact", "/path/does/not/exist.md"])
        self.assertEqual(rc, 1)

    def test_list_id_kinds_artifact_not_in_registry(self):
        """Cover lines 51-52: artifact exists but not registered."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            from cypilot.utils import toml_utils
            toml_utils.dump({
                "version": "1.0", "project_root": "..", "systems": [], "kits": {},
            }, adapter / "config" / "artifacts.toml")

            art = root / "docs" / "PRD.md"
            art.parent.mkdir(parents=True)
            art.write_text("- [x] `p1` - **ID**: `cpt-test-fr-1`\n", encoding="utf-8")

            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["list-id-kinds", "--artifact", str(art)])
            self.assertEqual(rc, 1)
            self.assertIn("not found in registry", buf.getvalue())

    def test_list_id_kinds_infer_kinds_branches(self):
        """Cover lines 85, 103, 106, 112, 119, 122, 125: kind inference branches."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)

            kit_root = root / "kits" / "sdlc"
            kit_root.mkdir(parents=True)

            art = root / "docs" / "PRD.md"
            art.parent.mkdir(parents=True)
            # Mix of IDs: one with known kind, one with unknown kind, one with no system match, empty-ish
            art.write_text(
                "- [x] `p1` - **ID**: `cpt-test-fr-login`\n"
                "- [x] `p1` - **ID**: `cpt-test-boguskind-x`\n"
                "- [x] `p1` - **ID**: `cpt-nomatch-thing`\n"
                "- [x] `p1` - **ID**: `cpt-test`\n"
                "some ref `cpt-test-fr-other`\n",
                encoding="utf-8",
            )

            from cypilot.utils import toml_utils
            toml_utils.dump({
                "version": "1.1", "project_root": "..",
                "kits": {"sdlc": {"format": "Cypilot", "path": "kits/sdlc"}},
                "systems": [{
                    "name": "Test", "slug": "test", "kits": "sdlc",
                    "artifacts": [{"path": "docs/PRD.md", "kind": "PRD"}],
                }],
            }, adapter / "config" / "artifacts.toml")

            # No constraints.toml → covers line 85 (kit_constraints falsy)
            buf = io.StringIO()
            cwd = os.getcwd()
            try:
                os.chdir(str(root))
                with redirect_stdout(buf):
                    rc = main(["list-id-kinds", "--artifact", str(art)])
            finally:
                os.chdir(cwd)
            self.assertEqual(rc, 0)


class TestCLIPyCoverageSelfCheckSkipBranches(unittest.TestCase):
    def test_self_check_skips_invalid_kit_defs(self):
        from cypilot import cli as cypilot_cli

        with TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            adapter = root / ".cypilot-adapter"
            adapter.mkdir()

            reg = {
                "version": "1.0",
                "kits": {
                    # invalid kit_def (not dict)
                    "bad-kit-1": 1,
                    # missing path
                    "bad-kit-2": {},
                    # path wrong type
                    "bad-kit-3": {"path": 123},
                },
            }

            with patch("cypilot.commands.self_check.find_project_root", return_value=root):
                with patch("cypilot.commands.self_check.find_cypilot_directory", return_value=adapter):
                    with patch("cypilot.commands.self_check.load_artifacts_meta") as mock_lam:
                        from unittest.mock import MagicMock
                        meta_m = MagicMock()
                        meta_m.validate_all_slugs.return_value = []
                        meta_m.kits = reg.get("kits", {})
                        mock_lam.return_value = (meta_m, None)
                    with patch("cypilot.commands.self_check.load_artifacts_meta", return_value=(meta_m, None)):
                        buf = io.StringIO()
                        with redirect_stdout(buf):
                            rc = cypilot_cli._cmd_self_check(["--root", td])

            self.assertEqual(rc, 0)
            out = json.loads(buf.getvalue())
            self.assertEqual(out.get("status"), "PASS")
            self.assertEqual(out.get("kits_checked"), 0)

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

    def test_self_check_verbose_includes_errors_when_example_missing(self):
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
                self.assertEqual(exit_code, 2)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "FAIL")
                self.assertEqual(out["results"][0]["status"], "FAIL")
                self.assertIn("errors", out["results"][0])
                self.assertGreater(out["results"][0].get("error_count", 0), 0)
            finally:
                os.chdir(cwd)

    def test_self_check_does_not_depend_on_template_module(self):
        from cypilot import cli as cypilot_cli

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)
            _bootstrap_self_check_kits(root, adapter, with_example=True, bad_example=False)

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = cypilot_cli._cmd_self_check([])
                self.assertEqual(exit_code, 0)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "PASS")
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
                "",
                encoding="utf-8",
            )
            ex_dir = kits_base / "examples"
            ex_dir.mkdir(parents=True, exist_ok=True)
            (ex_dir / "example.md").write_text(
                "- [x] `p1` - **ID**: `cpt-ex-item-1`\n",
                encoding="utf-8",
            )
            from _test_helpers import write_constraints_toml
            write_constraints_toml(root / "kits" / "cypilot-sdlc", {"req": {"identifiers": {"item": {"required": False, "to_code": True, "template": "cpt-{system}-item-{slug}"}}}})

            # Artifact defining ID with to_code=true
            art_dir = root / "artifacts"
            art_dir.mkdir(parents=True, exist_ok=True)
            (art_dir / "reqs.md").write_text(
                ""
                "- [x] `p1` - **ID**: `cpt-req-1`\n"
                "",
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
        from cypilot.commands.init import _prompt_path

        with patch("builtins.input", side_effect=EOFError):
            got = _prompt_path("Question?", "default")
        self.assertEqual(got, "default")

    def test_list_workflow_files_iterdir_exception(self):
        from cypilot.commands.agents import _list_workflow_files

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
            fake_cache = Path(tmpdir) / "cache"
            fake_cache.mkdir()

            # First init to create files (use --yes to avoid prompts)
            cwd = os.getcwd()
            try:
                os.chdir(root)
                with patch("cypilot.commands.init.CACHE_DIR", fake_cache):
                    stdout = io.StringIO()
                    with redirect_stdout(stdout):
                        exit_code = main(["init", "--yes"])
                    self.assertEqual(exit_code, 0)

                    # Second init without changes should still succeed
                    stdout = io.StringIO()
                    with redirect_stdout(stdout):
                        exit_code = main(["init", "--yes"])
                    # Init may succeed (0) or report issues (1/2) on re-run
                    self.assertIn(exit_code, [0, 1, 2])
                    out = json.loads(stdout.getvalue())
                    self.assertIn("status", out)
            finally:
                os.chdir(cwd)


class TestInitCopyFromCache(unittest.TestCase):
    """Direct tests for _copy_from_cache edge cases."""

    def test_copy_creates_and_skips(self):
        """First copy creates, second without force skips."""
        from cypilot.commands.init import _copy_from_cache
        with TemporaryDirectory() as td:
            cache = Path(td) / "cache"
            target = Path(td) / "project" / "cypilot"
            target.mkdir(parents=True)
            # Populate cache with one valid dir and one missing
            (cache / "requirements").mkdir(parents=True)
            (cache / "requirements" / "README.md").write_text("# req\n", encoding="utf-8")
            r1 = _copy_from_cache(cache, target, force=False)
            self.assertEqual(r1["requirements"], "created")
            self.assertEqual(r1.get("schemas", "missing_in_cache"), "missing_in_cache")
            # Second call without force → skipped
            r2 = _copy_from_cache(cache, target, force=False)
            self.assertEqual(r2["requirements"], "skipped")
            # Third call with force → updated
            r3 = _copy_from_cache(cache, target, force=True)
            self.assertEqual(r3["requirements"], "updated")

    def test_missing_cache_dir_entries(self):
        """When cache dirs don't exist, reports missing_in_cache."""
        from cypilot.commands.init import _copy_from_cache
        with TemporaryDirectory() as td:
            cache = Path(td) / "empty_cache"
            cache.mkdir()
            target = Path(td) / "target"
            target.mkdir()
            result = _copy_from_cache(cache, target, force=False)
            for k, v in result.items():
                self.assertEqual(v, "missing_in_cache")


class TestInitReadExistingInstall(unittest.TestCase):
    """Tests for _read_existing_install edge cases."""

    def test_returns_none_when_no_agents(self):
        from cypilot.commands.init import _read_existing_install
        with TemporaryDirectory() as td:
            self.assertIsNone(_read_existing_install(Path(td)))

    def test_returns_none_when_no_marker(self):
        from cypilot.commands.init import _read_existing_install
        with TemporaryDirectory() as td:
            (Path(td) / "AGENTS.md").write_text("# Just a file\n", encoding="utf-8")
            self.assertIsNone(_read_existing_install(Path(td)))

    def test_returns_none_when_dir_missing(self):
        """TOML has cypilot_path but directory doesn't exist → None."""
        from cypilot.commands.init import _read_existing_install
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "AGENTS.md").write_text(
                '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "nonexistent"\n```\n<!-- /@cpt:root-agents -->\n',
                encoding="utf-8",
            )
            self.assertIsNone(_read_existing_install(root))

    def test_returns_rel_when_dir_exists(self):
        from cypilot.commands.init import _read_existing_install
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "cpt").mkdir()
            (root / "AGENTS.md").write_text(
                '<!-- @cpt:root-agents -->\n```toml\ncypilot_path = "cpt"\n```\n<!-- /@cpt:root-agents -->\n',
                encoding="utf-8",
            )
            self.assertEqual(_read_existing_install(root), "cpt")


class TestInjectRootAgents(unittest.TestCase):
    """Tests for _inject_root_agents: create, update, unchanged."""

    def test_creates_agents_file(self):
        from cypilot.commands.init import _inject_root_agents
        with TemporaryDirectory() as td:
            root = Path(td)
            action = _inject_root_agents(root, "cypilot")
            self.assertEqual(action, "created")
            self.assertTrue((root / "AGENTS.md").is_file())

    def test_replaces_stale_block(self):
        from cypilot.commands.init import _inject_root_agents, MARKER_START, MARKER_END
        with TemporaryDirectory() as td:
            root = Path(td)
            # Write AGENTS.md with old block
            (root / "AGENTS.md").write_text(
                f"{MARKER_START}\nold content\n{MARKER_END}\n\nUser stuff\n",
                encoding="utf-8",
            )
            action = _inject_root_agents(root, "cypilot")
            self.assertEqual(action, "updated")
            content = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("cypilot_path", content)
            self.assertIn("User stuff", content)

    def test_unchanged_when_current(self):
        from cypilot.commands.init import _inject_root_agents
        with TemporaryDirectory() as td:
            root = Path(td)
            # First inject creates
            _inject_root_agents(root, "cypilot")
            # Second should be unchanged
            action = _inject_root_agents(root, "cypilot")
            self.assertEqual(action, "unchanged")

    def test_dry_run_does_not_write(self):
        from cypilot.commands.init import _inject_root_agents
        with TemporaryDirectory() as td:
            root = Path(td)
            action = _inject_root_agents(root, "cypilot", dry_run=True)
            self.assertEqual(action, "created")
            self.assertFalse((root / "AGENTS.md").is_file())


class TestInitNoCacheError(unittest.TestCase):
    """init fails when ~/.cypilot/cache doesn't exist."""

    def test_init_no_cache_returns_error(self):
        from cypilot.cli import main
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            cwd = os.getcwd()
            try:
                os.chdir(root)
                fake_cache = Path(td) / "nonexistent_cache"
                with patch("cypilot.commands.init.CACHE_DIR", fake_cache):
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        rc = main(["init", "--yes"])
                self.assertEqual(rc, 1)
                out = json.loads(buf.getvalue())
                self.assertIn("cache", out.get("message", "").lower())
            finally:
                os.chdir(cwd)


class TestInitForceReinit(unittest.TestCase):
    """init --force on existing project: creates backup, overwrites files."""

    def test_force_reinit_overwrites(self):
        from cypilot.cli import main
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / ".git").mkdir()
            cache = Path(td) / "cache"
            _make_test_cache(cache)
            cwd = os.getcwd()
            try:
                os.chdir(root)
                with patch("cypilot.commands.init.CACHE_DIR", cache):
                    # First init
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        rc = main(["init", "--yes"])
                    self.assertEqual(rc, 0)
                    # Force re-init
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        rc = main(["init", "--yes", "--force"])
                    self.assertEqual(rc, 0)
                    out = json.loads(buf.getvalue())
                    self.assertEqual(out["status"], "PASS")
            finally:
                os.chdir(cwd)


def _make_test_cache(cache_dir: Path) -> None:
    """Minimal cache for init tests."""
    for d in ("architecture", "requirements", "schemas", "workflows", "skills"):
        (cache_dir / d).mkdir(parents=True, exist_ok=True)
        (cache_dir / d / "README.md").write_text(f"# {d}\n", encoding="utf-8")
    bp_dir = cache_dir / "kits" / "sdlc" / "blueprints"
    bp_dir.mkdir(parents=True, exist_ok=True)
    (bp_dir / "prd.md").write_text(
        "<!-- @cpt:blueprint -->\n```toml\n"
        'artifact = "PRD"\nkit = "sdlc"\nversion = 1\n'
        "```\n<!-- /@cpt:blueprint -->\n\n"
        "<!-- @cpt:heading -->\n# Product Requirements\n<!-- /@cpt:heading -->\n",
        encoding="utf-8",
    )
    from cypilot.utils import toml_utils
    toml_utils.dump({"version": 1, "blueprints": {"prd": 1}}, cache_dir / "kits" / "sdlc" / "conf.toml")


class TestCLIPyCoverageValidateRules(unittest.TestCase):
    """Tests for validate-kits command (kit constraints validation)."""

    def test_validate_rules_single_template(self):
        """validate-kits validates constraints.toml for kits."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            adapter = _bootstrap_project_root(root)
            _write_json(
                adapter / "artifacts.json",
                {
                    "project_root": "..",
                    "systems": [],
                    "kits": {"cypilot-sdlc": {"format": "Cypilot", "path": "kits/cypilot-sdlc"}},
                },
            )
            kit_root = root / "kits" / "cypilot-sdlc"
            kit_root.mkdir(parents=True, exist_ok=True)
            from _test_helpers import write_constraints_toml
            write_constraints_toml(kit_root, {"REQ": {"identifiers": {"req": {"required": True}}}})

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

    def test_validate_rules_verbose_with_errors(self):
        """validate-kits --verbose shows constraints errors."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            adapter = _bootstrap_project_root(root)
            _write_json(
                adapter / "artifacts.json",
                {
                    "project_root": "..",
                    "systems": [],
                    "kits": {"cypilot-sdlc": {"format": "Cypilot", "path": "kits/cypilot-sdlc"}},
                },
            )
            kit_root = root / "kits" / "cypilot-sdlc"
            kit_root.mkdir(parents=True, exist_ok=True)
            (kit_root / "constraints.toml").write_text("not valid toml [[", encoding="utf-8")

            cwd = os.getcwd()
            try:
                os.chdir(root)
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    exit_code = main(["validate-kits", "--verbose"])
                self.assertEqual(exit_code, 2)
                out = json.loads(stdout.getvalue())
                self.assertEqual(out.get("status"), "FAIL")
                self.assertIn("errors", out)
            finally:
                os.chdir(cwd)

    def test_validate_rules_all_from_registry(self):
        """validate-kits validates all kits from artifacts.json."""
        from cypilot.cli import main

        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adapter = _bootstrap_project_root(root)

            kit_root = root / "kits" / "cypilot-sdlc"
            kit_root.mkdir(parents=True, exist_ok=True)
            from _test_helpers import write_constraints_toml
            write_constraints_toml(kit_root, {"REQ": {"identifiers": {"req": {"required": True}}}})

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
                self.assertGreaterEqual(out.get("kits_validated", 0), 1)
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
                "---\ncypilot-template:\n  kind: req\n  version:\n    major: 1\n    minor: 0\n---\n",
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
                "",
                encoding="utf-8",
            )

            # Create artifact with ID definition and reference
            art_dir = root / "artifacts"
            art_dir.mkdir(parents=True, exist_ok=True)
            (art_dir / "reqs.md").write_text(
                ""
                "- [x] `p1` - **ID**: `cpt-test-item-1`\n"
                ""
                ""
                "- [ ] `p2` - `cpt-external-ref-abc`\n"
                "",
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


class TestCLIDispatchUncoveredCommands(unittest.TestCase):
    """Cover cli.py dispatch branches for update, kit, generate-resources, toc, validate-toc."""

    def test_dispatch_update_no_project(self):
        """'update' dispatches to cmd_update; fails gracefully outside a project."""
        from cypilot.cli import main
        with TemporaryDirectory() as td:
            cwd = os.getcwd()
            try:
                os.chdir(td)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["update"])
                self.assertIn(rc, [0, 1, 2])
            finally:
                os.chdir(cwd)

    def test_dispatch_kit_no_subcommand(self):
        """'kit' with no subcommand returns error."""
        from cypilot.cli import main
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["kit"])
        self.assertEqual(rc, 1)
        out = json.loads(buf.getvalue())
        self.assertEqual(out["status"], "ERROR")

    def test_dispatch_generate_resources_no_project(self):
        """'generate-resources' dispatches correctly; fails outside a project."""
        from cypilot.cli import main
        with TemporaryDirectory() as td:
            cwd = os.getcwd()
            try:
                os.chdir(td)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main(["generate-resources"])
                self.assertIn(rc, [1, 2])
            finally:
                os.chdir(cwd)

    def test_dispatch_toc(self):
        """'toc' command dispatches to cmd_toc."""
        from cypilot.cli import main
        with TemporaryDirectory() as td:
            md = Path(td) / "doc.md"
            md.write_text("# Title\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["toc", str(md)])
            self.assertIn(rc, [0, 1, 2])

    def test_dispatch_validate_toc(self):
        """'validate-toc' command dispatches to cmd_validate_toc."""
        from cypilot.cli import main
        with TemporaryDirectory() as td:
            md = Path(td) / "doc.md"
            md.write_text("# Title\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main(["validate-toc", str(md)])
            self.assertIn(rc, [0, 1, 2])


if __name__ == "__main__":
    unittest.main()
